from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.models import Order as OrderModel, OrderItem as OrderItemModel, Product as ProductModel, User as UserModel
from app.schemas.schemas import OrderCreate, OrderUpdate, Order
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, request: Request, db: Session = Depends(get_db)):
    # Try to get current user (optional)
    current_user = None
    
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        current_user = get_current_user(db, token)
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Calculate total amount
    total_amount = 0
    order_items = []
    
    for item in order.items:
        # Check if product exists and has enough stock
        db_product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if db_product is None:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")
        
        if db_product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {db_product.name}")
        
        # Calculate item price
        item_price = db_product.price * item.quantity
        total_amount += item_price
        
        # Create order item
        order_item = OrderItemModel(
            product_id=item.product_id,
            quantity=item.quantity,
            price=db_product.price
        )
        order_items.append(order_item)
        
        # Update product stock
        db_product.stock_quantity -= item.quantity
    
    # Create order
    db_order = OrderModel(
        user_id=current_user.id,
        total_amount=total_amount,
        status="pending",
        payment_method=order.payment_method,
        bank=order.bank
        # created_at=order.created_at
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Add order items
    for item in order_items:
        item.order_id = db_order.id
        db.add(item)
    
    db.commit()
    db.refresh(db_order)
    
    # Load order items for response
    db_order.items = order_items
    
    return db_order

@router.get("/", response_model=List[Order])
def read_orders(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Try to get current user (optional)
    current_user = None
    
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        current_user = get_current_user(db, token)
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # If user is admin, return all orders, otherwise return only user's orders
    if current_user.is_admin:
        orders = db.query(OrderModel).order_by(OrderModel.id).offset(skip).limit(limit).all()
    else:
        orders = db.query(OrderModel).filter(OrderModel.user_id == current_user.id).order_by(OrderModel.id).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=Order)
def read_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    # Try to get current user (optional)
    current_user = None
    
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        current_user = get_current_user(db, token)
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user is authorized to access this order
    if not current_user.is_admin and db_order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this order")
    
    return db_order

@router.put("/{order_id}", response_model=Order)
def update_order(order_id: int, order: OrderUpdate, request: Request, db: Session = Depends(get_db)):
    # Try to get current user (optional)
    current_user = None
    
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        current_user = get_current_user(db, token)
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user is authorized to update this order
    if not current_user.is_admin and db_order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this order")
    
    db_order.status = order.status
    # db_order.updated_at = order.updated_at
    db.commit()
    db.refresh(db_order)
    return db_order