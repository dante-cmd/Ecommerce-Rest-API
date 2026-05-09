from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

from app.database.database import get_db
from app.database.mongodb import get_reviews_collection
from app.models.models import Product as ProductModel, User as UserModel, Order as OrderModel, OrderItem as OrderItemModel
from app.schemas.reviews import ReviewCreate, ReviewUpdate, Review
from app.core.auth import get_current_user

router = APIRouter()


def _to_review_response(doc: dict) -> dict:
    """Convert a MongoDB document to a review response dict."""
    doc["id"] = str(doc.pop("_id"))
    return doc


def _check_product_exists(db: Session, product_id: int):
    """Validate that a product exists in MSSQL."""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
    return product


def _check_verified_purchase(db: Session, user_id: int, product_id: int) -> bool:
    """Check if the user has purchased this product."""
    order_items = (
        db.query(OrderItemModel)
        .join(OrderModel)
        .filter(
            OrderModel.user_id == user_id,
            OrderItemModel.product_id == product_id,
        )
        .first()
    )
    return order_items is not None


@router.post("/", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(
    review: ReviewCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    # Authenticate user
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    current_user = get_current_user(db, token)

    # Validate product exists in MSSQL
    _check_product_exists(db, review.product_id)

    # Check if user already reviewed this product
    collection = get_reviews_collection()
    existing = collection.find_one({
        "product_id": review.product_id,
        "user_id": current_user.id,
    })
    if existing:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this product"
        )

    # Determine verified purchase
    verified = _check_verified_purchase(db, current_user.id, review.product_id)

    now = datetime.utcnow()
    doc = {
        "product_id": review.product_id,
        "user_id": current_user.id,
        "rating": review.rating,
        "title": review.title,
        "content": review.content,
        "images": review.images or [],
        "helpful_votes": 0,
        "verified_purchase": verified,
        "created_at": now,
        "updated_at": None,
    }
    result = collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _to_review_response(doc)


@router.get("/product/{product_id}", response_model=List[Review])
def read_reviews_by_product(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    # Validate product exists in MSSQL
    _check_product_exists(db, product_id)

    collection = get_reviews_collection()
    cursor = (
        collection.find({"product_id": product_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return [_to_review_response(doc) for doc in cursor]


@router.get("/user/{user_id}", response_model=List[Review])
def read_reviews_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    # Validate user exists in MSSQL
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    collection = get_reviews_collection()
    cursor = (
        collection.find({"user_id": user_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return [_to_review_response(doc) for doc in cursor]


@router.get("/{review_id}", response_model=Review)
def read_review(review_id: str):
    collection = get_reviews_collection()
    try:
        doc = collection.find_one({"_id": ObjectId(review_id)})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid review id")

    if doc is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return _to_review_response(doc)


@router.put("/{review_id}", response_model=Review)
def update_review(
    review_id: str,
    review: ReviewUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    # Authenticate user
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    current_user = get_current_user(db, token)

    collection = get_reviews_collection()
    try:
        doc = collection.find_one({"_id": ObjectId(review_id)})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid review id")

    if doc is None:
        raise HTTPException(status_code=404, detail="Review not found")

    # Only the author or an admin can update
    if doc["user_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this review")

    update_data = {}
    if review.rating is not None:
        update_data["rating"] = review.rating
    if review.title is not None:
        update_data["title"] = review.title
    if review.content is not None:
        update_data["content"] = review.content
    if review.images is not None:
        update_data["images"] = review.images
    update_data["updated_at"] = datetime.utcnow()

    collection.update_one({"_id": ObjectId(review_id)}, {"$set": update_data})
    doc.update(update_data)
    return _to_review_response(doc)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    # Authenticate user
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    current_user = get_current_user(db, token)

    collection = get_reviews_collection()
    try:
        doc = collection.find_one({"_id": ObjectId(review_id)})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid review id")

    if doc is None:
        raise HTTPException(status_code=404, detail="Review not found")

    # Only the author or an admin can delete
    if doc["user_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")

    collection.delete_one({"_id": ObjectId(review_id)})
    return None


@router.post("/{review_id}/helpful", response_model=Review)
def mark_helpful(review_id: str):
    collection = get_reviews_collection()
    try:
        result = collection.update_one(
            {"_id": ObjectId(review_id)},
            {"$inc": {"helpful_votes": 1}}
        )
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid review id")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")

    doc = collection.find_one({"_id": ObjectId(review_id)})
    return _to_review_response(doc)
