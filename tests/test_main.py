import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the E-commerce API"}

def test_create_product():
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 29.99,
        "category": "test",
        "stock_quantity": 100,
        "is_available": True
    }
    response = client.post("/api/products/", json=product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]
    assert "id" in data

def test_read_products():
    response = client.get("/api/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)