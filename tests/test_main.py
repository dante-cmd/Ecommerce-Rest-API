"""
Complete test suite for the E-commerce REST API.

Strategy:
- Uses an in-memory SQLite database so tests are fully self-contained
  (no SQL Server required).
- Overrides the `get_db` dependency so every test gets a clean session.
- Tests are ordered with pytest-ordering or plain alphabetical execution;
  shared state is managed through module-level fixtures / IDs captured in
  helper variables.

Run with:
    pytest tests/test_main.py -v
"""

import pytest
from datetime import datetime
import json
from fastapi.testclient import TestClient

# For DB direct access in tests
from app.models import models

# ---------------------------------------------------------------------------
# Shared state between tests (populated as fixtures run)
# ---------------------------------------------------------------------------
_state: dict = {}


# ===========================================================================
# Helper
# ===========================================================================

def _auth_headers(client: TestClient, email: str, password: str) -> dict:
    r = client.post("/api/users/token", json={"email": email, "password": password})
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# 1. Root
# ===========================================================================

class TestRoot:
    def test_root_returns_welcome_message(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json() == {"message": "Welcome to the E-commerce API"}


# ===========================================================================
# 2. Users
# ===========================================================================

class TestUsers:
    BASE = "/api/users"

    def test_create_user(self, client):
        payload = {
            "email": "alice@example.com",
            "username": "alice",
            "full_name": "Alice Example",
            "password": "secret123",
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        assert "id" in data
        _state["user_id"] = data["id"]
        _state["user_email"] = payload["email"]
        _state["user_password"] = payload["password"]

    def test_create_duplicate_user_fails(self, client):
        payload = {
            "email": "alice@example.com",
            "username": "alice2",
            "full_name": "Alice Dup",
            "password": "secret123",
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 400
        assert "already registered" in r.json()["detail"].lower()

    def test_create_admin_user(self, client):
        """Create a second user that we'll promote to admin directly in DB."""
        payload = {
            "email": "admin@example.com",
            "username": "adminuser",
            "full_name": "Admin User",
            "password": "adminpass",
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 201, r.text
        admin_id = r.json()["id"]
        _state["admin_id"] = admin_id
        _state["admin_email"] = payload["email"]
        _state["admin_password"] = payload["password"]

        # Promote to admin directly in the DB
        # Use the test database sessionmaker
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///./test_ecommerce.db", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = TestingSessionLocal()
        try:
            user = db.query(models.User).filter(models.User.id == admin_id).first()
            user.is_admin = True  # type: ignore[union-attr]
            db.commit()
        finally:
            db.close()

    def test_read_users_list(self, client):
        r = client.get(self.BASE + "/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) >= 1

    def test_read_user_by_id(self, client):
        r = client.get(f"{self.BASE}/{_state['user_id']}")
        assert r.status_code == 200
        assert r.json()["id"] == _state["user_id"]

    def test_read_user_by_id_not_found(self, client):
        r = client.get(f"{self.BASE}/999999")
        assert r.status_code == 404

    def test_read_user_by_email(self, client):
        r = client.get(f"{self.BASE}/email/{_state['user_email']}")
        assert r.status_code == 200
        assert r.json()["email"] == _state["user_email"]

    def test_read_user_by_email_not_found(self, client):
        r = client.get(f"{self.BASE}/email/nobody@nowhere.com")
        assert r.status_code == 404

    def test_login_returns_token(self, client):
        r = client.post(
            self.BASE + "/token",
            json={"email": _state["user_email"], "password": _state["user_password"]},
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        r = client.post(
            self.BASE + "/token",
            json={"email": _state["user_email"], "password": "wrongpassword"},
        )
        assert r.status_code == 401

    def test_login_without_password(self, client):
        r = client.post(
            self.BASE + "/token_without_password",
            json={"email": _state["user_email"]},
        )
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_login_without_password_unknown_email(self, client):
        r = client.post(
            self.BASE + "/token_without_password",
            json={"email": "ghost@example.com"},
        )
        assert r.status_code == 401


# ===========================================================================
# 3. IP Addresses
# ===========================================================================

class TestIPAddresses:
    BASE = "/api/ip_address"

    def test_create_ip_address(self, client):
        r = client.post(self.BASE + "/", json={"ip_address": "192.168.1.100"})
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["ip_address"] == "192.168.1.100"
        assert "id" in data
        _state["ip_id"] = data["id"]
        _state["ip_addr"] = data["ip_address"]

    def test_create_second_ip_address(self, client):
        """Extra IP used by cart/interaction tests."""
        r = client.post(self.BASE + "/", json={"ip_address": "10.0.0.1"})
        assert r.status_code == 201, r.text
        _state["ip_id_2"] = r.json()["id"]

    def test_create_duplicate_ip_fails(self, client):
        r = client.post(self.BASE + "/", json={"ip_address": "192.168.1.100"})
        assert r.status_code == 400

    def test_read_ip_by_address(self, client):
        r = client.get(f"{self.BASE}/{_state['ip_addr']}")
        assert r.status_code == 200
        assert r.json()["ip_address"] == _state["ip_addr"]

    def test_read_ip_not_found(self, client):
        r = client.get(f"{self.BASE}/0.0.0.0")
        assert r.status_code == 404


# ===========================================================================
# 4. User-IP Associations
# ===========================================================================

class TestUserIPAddress:
    BASE = "/api/user_ip_address"

    def test_associate_user_with_ip(self, client):
        payload = {
            "user_id": _state["user_id"],
            "ip_address_id": _state["ip_id"],
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["user_id"] == _state["user_id"]
        assert data["ip_address_id"] == _state["ip_id"]

    def test_associate_duplicate_ip_fails(self, client):
        payload = {
            "user_id": _state["user_id"],
            "ip_address_id": _state["ip_id"],
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 400

    def test_read_user_ip_by_id(self, client):
        r = client.get(f"{self.BASE}/{_state['ip_id']}")
        assert r.status_code == 200
        assert r.json()["ip_address_id"] == _state["ip_id"]

    def test_read_user_ip_not_found(self, client):
        r = client.get(f"{self.BASE}/999999")
        assert r.status_code == 404


# ===========================================================================
# 5. Products
# ===========================================================================

class TestProducts:
    BASE = "/api/products"

    def test_create_product(self, client):
        payload = {
            "name": "Test Widget",
            "description": "A handy widget for testing",
            "price": 19.99,
            "category": "widgets",
            "stock_quantity": 50,
            "is_available": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["name"] == payload["name"]
        assert data["price"] == payload["price"]
        assert "id" in data
        _state["product_id"] = data["id"]

    def test_create_second_product(self, client):
        """Used for order tests."""
        payload = {
            "name": "Another Widget",
            "description": "Second product",
            "price": 9.99,
            "category": "widgets",
            "stock_quantity": 20,
            "is_available": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 201, r.text
        _state["product_id_2"] = r.json()["id"]

    def test_read_products_list(self, client):
        r = client.get(self.BASE + "/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) >= 1

    def test_read_product_by_id(self, client):
        r = client.get(f"{self.BASE}/{_state['product_id']}")
        assert r.status_code == 200
        assert r.json()["id"] == _state["product_id"]

    def test_read_product_not_found(self, client):
        r = client.get(f"{self.BASE}/999999")
        assert r.status_code == 404

    def test_update_product(self, client):
        payload = {"name": "Updated Widget", "price": 24.99}
        r = client.put(f"{self.BASE}/{_state['product_id']}", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["name"] == "Updated Widget"
        assert data["price"] == 24.99

    def test_update_product_not_found(self, client):
        payload = {"name": "Ghost"}
        r = client.put(f"{self.BASE}/999999", json=payload)
        assert r.status_code == 404

    def test_delete_product(self, client):
        # Create a throwaway product
        payload = {
            "name": "Delete Me",
            "description": "Ephemeral",
            "price": 1.00,
            "category": "trash",
            "stock_quantity": 1,
            "is_available": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 201
        pid = r.json()["id"]

        r = client.delete(f"{self.BASE}/{pid}")
        assert r.status_code == 204

        # Confirm it's gone
        r = client.get(f"{self.BASE}/{pid}")
        assert r.status_code == 404

    def test_delete_product_not_found(self, client):
        r = client.delete(f"{self.BASE}/999999")
        assert r.status_code == 404


# ===========================================================================
# 6. Cart
# ===========================================================================

class TestCart:
    BASE = "/api/cart"

    def test_add_item_to_cart(self, client):
        payload = {
            "ip_address_id": _state["ip_id"],
            "product_id": _state["product_id"],
            "quantity": 2,
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["product_id"] == _state["product_id"]
        assert data["quantity"] == 2
        _state["cart_item_id"] = data["id"]

    def test_add_same_item_increases_quantity(self, client):
        payload = {
            "ip_address_id": _state["ip_id"],
            "product_id": _state["product_id"],
            "quantity": 1,
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 201, r.text
        assert r.json()["quantity"] == 3  # 2 + 1

    def test_add_item_product_not_found(self, client):
        payload = {
            "ip_address_id": _state["ip_id"],
            "product_id": 999999,
            "quantity": 1,
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 404

    def test_add_item_insufficient_stock(self, client):
        payload = {
            "ip_address_id": _state["ip_id"],
            "product_id": _state["product_id"],
            "quantity": 100000,
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 400

    def test_read_cart_by_ip(self, client):
        r = client.get(f"{self.BASE}/{_state['ip_id']}")
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert len(items) >= 1

    def test_read_empty_cart(self, client):
        r = client.get(f"{self.BASE}/{_state['ip_id_2']}")
        assert r.status_code == 200
        assert r.json() == []

    def test_update_cart_item(self, client):
        payload = {
            "id": _state["cart_item_id"],
            "ip_address_id": _state["ip_id"],
            "product_id": _state["product_id"],
            "quantity": 5,
        }
        r = client.put(self.BASE + "/", json=payload)
        assert r.status_code == 200, r.text
        assert r.json()["quantity"] == 5

    def test_update_cart_item_not_found(self, client):
        payload = {
            "id": 999999,
            "ip_address_id": _state["ip_id"],
            "product_id": _state["product_id"],
            "quantity": 1,
        }
        r = client.put(self.BASE + "/", json=payload)
        assert r.status_code == 404

    def test_delete_cart_item(self, client):
        # Add a throwaway cart item first
        payload = {
            "ip_address_id": _state["ip_id_2"],
            "product_id": _state["product_id_2"],
            "quantity": 1,
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 201
        item_id = r.json()["id"]

        # TestClient.delete does not support json=, so use data and headers
        delete_payload = json.dumps({"id": item_id, "ip_address_id": _state["ip_id_2"]})
        r = client.request(
            "DELETE",
            self.BASE + "/",
            content=delete_payload,
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 204

    def test_delete_cart_item_not_found(self, client):
        delete_payload = json.dumps({"id": 999999, "ip_address_id": _state["ip_id"]})
        r = client.request(
            "DELETE",
            self.BASE + "/",
            content=delete_payload,
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 404


# ===========================================================================
# 7. Orders  (require Bearer token)
# ===========================================================================

class TestOrders:
    BASE = "/api/orders"

    def test_create_order_unauthenticated(self, client):
        payload = {
            "items": [{"product_id": _state["product_id"], "quantity": 1}]
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 401

    def test_create_order_authenticated(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        payload = {
            "items": [{"product_id": _state["product_id_2"], "quantity": 1}],
            "payment_method": "credit_card",
            "bank": "Visa",
        }
        r = client.post(self.BASE + "/", json=payload, headers=headers)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["user_id"] == _state["user_id"]
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        _state["order_id"] = data["id"]

    def test_create_order_product_not_found(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        payload = {"items": [{"product_id": 999999, "quantity": 1}]}
        r = client.post(self.BASE + "/", json=payload, headers=headers)
        assert r.status_code == 404

    def test_create_order_insufficient_stock(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        payload = {
            "items": [{"product_id": _state["product_id_2"], "quantity": 100000}]
        }
        r = client.post(self.BASE + "/", json=payload, headers=headers)
        assert r.status_code == 400

    def test_read_orders_unauthenticated(self, client):
        r = client.get(self.BASE + "/")
        assert r.status_code == 401

    def test_read_orders_authenticated(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        r = client.get(self.BASE + "/", headers=headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) >= 1

    def test_read_order_by_id(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        r = client.get(f"{self.BASE}/{_state['order_id']}", headers=headers)
        assert r.status_code == 200
        assert r.json()["id"] == _state["order_id"]

    def test_read_order_not_found(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        r = client.get(f"{self.BASE}/999999", headers=headers)
        assert r.status_code == 404

    def test_update_order_status(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        r = client.put(
            f"{self.BASE}/{_state['order_id']}",
            json={"status": "confirmed"},
            headers=headers,
        )
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "confirmed"

    def test_update_order_not_found(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        r = client.put(
            f"{self.BASE}/999999",
            json={"status": "confirmed"},
            headers=headers,
        )
        assert r.status_code == 404

    def test_admin_can_read_all_orders(self, client):
        headers = _auth_headers(client, _state["admin_email"], _state["admin_password"])
        r = client.get(self.BASE + "/", headers=headers)
        assert r.status_code == 200
        # Admin sees every order, including the ones created by alice
        all_ids = [o["id"] for o in r.json()]
        assert _state["order_id"] in all_ids


# ===========================================================================
# 8. Interactions
# ===========================================================================

class TestInteractions:
    BASE = "/api/interactions"

    def test_create_interaction(self, client):
        payload = {
            "ip_address_id": _state["ip_id"],
            "interaction_type": "view",
            "interaction_metadata": '{"product_id": 1}',
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["interaction_type"] == "view"
        assert "id" in data
        _state["interaction_id"] = data["id"]

    def test_create_interaction_without_metadata(self, client):
        payload = {
            "ip_address_id": _state["ip_id"],
            "interaction_type": "click",
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 201, r.text
        assert r.json()["interaction_metadata"] is None

    def test_read_interactions_requires_admin(self, client):
        """Regular user should be denied (403)."""
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        r = client.get(self.BASE + "/", headers=headers)
        assert r.status_code == 403

    def test_read_interactions_as_admin(self, client):
        headers = _auth_headers(client, _state["admin_email"], _state["admin_password"])
        r = client.get(self.BASE + "/", headers=headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) >= 1

    def test_read_interaction_by_id_as_admin(self, client):
        headers = _auth_headers(client, _state["admin_email"], _state["admin_password"])
        r = client.get(f"{self.BASE}/{_state['interaction_id']}", headers=headers)
        assert r.status_code == 200
        assert r.json()["id"] == _state["interaction_id"]

    def test_read_interaction_not_found(self, client):
        headers = _auth_headers(client, _state["admin_email"], _state["admin_password"])
        r = client.get(f"{self.BASE}/999999", headers=headers)
        assert r.status_code == 404

    def test_read_interactions_unauthenticated(self, client):
        r = client.get(self.BASE + "/")
        assert r.status_code in (401, 403)


# ===========================================================================
# 9. Reviews (MongoDB)
# ===========================================================================

class TestReviews:
    BASE = "/api/reviews"

    def test_create_review_unauthenticated(self, client):
        payload = {
            "product_id": _state["product_id"],
            "rating": 5,
            "title": "Great product",
            "content": "I love this product!",
        }
        r = client.post(self.BASE + "/", json=payload)
        assert r.status_code == 401

    def test_create_review_authenticated(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        payload = {
            "product_id": _state["product_id"],
            "rating": 5,
            "title": "Great product",
            "content": "I love this product!",
            "images": ["http://example.com/img1.jpg"],
        }
        r = client.post(self.BASE + "/", json=payload, headers=headers)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["product_id"] == _state["product_id"]
        assert data["user_id"] == _state["user_id"]
        assert data["rating"] == 5
        assert data["title"] == "Great product"
        assert data["content"] == "I love this product!"
        assert data["images"] == ["http://example.com/img1.jpg"]
        assert data["helpful_votes"] == 0
        assert "id" in data
        _state["review_id"] = data["id"]

    def test_create_review_duplicate_fails(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        payload = {
            "product_id": _state["product_id"],
            "rating": 4,
            "title": "Another review",
            "content": "Should fail",
        }
        r = client.post(self.BASE + "/", json=payload, headers=headers)
        assert r.status_code == 400
        assert "already reviewed" in r.json()["detail"].lower()

    def test_create_review_product_not_found(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        payload = {
            "product_id": 999999,
            "rating": 5,
            "title": "Ghost product",
            "content": "Should fail",
        }
        r = client.post(self.BASE + "/", json=payload, headers=headers)
        assert r.status_code == 404

    def test_read_reviews_by_product(self, client):
        r = client.get(f"{self.BASE}/product/{_state['product_id']}")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["product_id"] == _state["product_id"]

    def test_read_reviews_by_product_not_found(self, client):
        r = client.get(f"{self.BASE}/product/999999")
        assert r.status_code == 404

    def test_read_reviews_by_user(self, client):
        r = client.get(f"{self.BASE}/user/{_state['user_id']}")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["user_id"] == _state["user_id"]

    def test_read_reviews_by_user_not_found(self, client):
        r = client.get(f"{self.BASE}/user/999999")
        assert r.status_code == 404

    def test_read_review_by_id(self, client):
        r = client.get(f"{self.BASE}/{_state['review_id']}")
        assert r.status_code == 200
        assert r.json()["id"] == _state["review_id"]

    def test_read_review_not_found(self, client):
        r = client.get(f"{self.BASE}/000000000000000000000000")
        assert r.status_code == 404

    def test_read_review_invalid_id(self, client):
        r = client.get(f"{self.BASE}/not-an-object-id")
        assert r.status_code == 400

    def test_update_review(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        payload = {"rating": 4, "title": "Updated title", "content": "Updated content"}
        r = client.put(f"{self.BASE}/{_state['review_id']}", json=payload, headers=headers)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["rating"] == 4
        assert data["title"] == "Updated title"
        assert data["content"] == "Updated content"

    def test_update_review_not_found(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        payload = {"rating": 3}
        r = client.put(f"{self.BASE}/000000000000000000000000", json=payload, headers=headers)
        assert r.status_code == 404

    def test_update_review_unauthorized(self, client):
        # Admin creates a review for product_2
        admin_headers = _auth_headers(client, _state["admin_email"], _state["admin_password"])
        payload = {
            "product_id": _state["product_id_2"],
            "rating": 5,
            "title": "Admin review",
            "content": "Admin content",
        }
        r = client.post(self.BASE + "/", json=payload, headers=admin_headers)
        assert r.status_code == 201
        admin_review_id = r.json()["id"]

        # Regular user tries to update admin's review
        user_headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        payload = {"rating": 1}
        r = client.put(f"{self.BASE}/{admin_review_id}", json=payload, headers=user_headers)
        assert r.status_code == 403

    def test_mark_review_helpful(self, client):
        r = client.post(f"{self.BASE}/{_state['review_id']}/helpful")
        assert r.status_code == 200, r.text
        assert r.json()["helpful_votes"] == 1

        r = client.post(f"{self.BASE}/{_state['review_id']}/helpful")
        assert r.status_code == 200
        assert r.json()["helpful_votes"] == 2

    def test_delete_review_unauthorized(self, client):
        # Try to delete admin's review as regular user
        # First get admin review id from previous test
        # Actually we need to create one fresh
        admin_headers = _auth_headers(client, _state["admin_email"], _state["admin_password"])
        payload = {
            "product_id": _state["product_id_2"],
            "rating": 5,
            "title": "To delete",
            "content": "Content",
        }
        r = client.post(self.BASE + "/", json=payload, headers=admin_headers)
        # Duplicate may fail since admin already reviewed product_2 above
        if r.status_code == 201:
            admin_review_id = r.json()["id"]
        else:
            # Find existing admin review
            r = client.get(f"{self.BASE}/user/{_state['admin_id']}")
            admin_review_id = r.json()[0]["id"]

        user_headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        r = client.delete(f"{self.BASE}/{admin_review_id}", headers=user_headers)
        assert r.status_code == 403

    def test_delete_review(self, client):
        headers = _auth_headers(client, _state["user_email"], _state["user_password"])
        r = client.delete(f"{self.BASE}/{_state['review_id']}", headers=headers)
        assert r.status_code == 204

        r = client.get(f"{self.BASE}/{_state['review_id']}")
        assert r.status_code == 404


# ===========================================================================
# Teardown – drop all tables after the whole test session
# ===========================================================================
# (Cleanup is handled by conftest.py)