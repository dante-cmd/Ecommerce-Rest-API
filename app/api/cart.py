from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.models import CartItem as CartItemModel, Product as ProductModel, User as UserModel
from app.schemas.schemas import CartItemCreate, CartItemUpdate, CartItem, CartItemDelete
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=CartItem, status_code=status.HTTP_201_CREATED)
def add_to_cart(cart_item: CartItemCreate,
                db: Session = Depends(get_db)
                ):

    # Try to get current user (optional)
    # current_user = None
    
    # Get token from Authorization header
    # auth_header = request.headers.get("Authorization")
    # if auth_header and auth_header.startswith("Bearer "):
    #     token = auth_header.split(" ")[1]
    #     current_user = get_current_user(db, token)
    # else:
    #     raise HTTPException(status_code=401, detail="Not authenticated")

    # Check if product exists
    db_product = db.query(ProductModel).filter(
        ProductModel.id == cart_item.product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if product has enough stock
    if db_product.stock_quantity < cart_item.quantity: # type: ignore
        raise HTTPException(status_code=400, detail="Not enough stock for this product")
    
    # Check if item already in cart
    db_cart_item = db.query(CartItemModel).filter(
        CartItemModel.ip_address_id == cart_item.ip_address_id,
        CartItemModel.product_id == cart_item.product_id
    ).first()
    
    if db_cart_item:
        # Update quantity
        db_cart_item.quantity += cart_item.quantity # type: ignore
        if db_cart_item.quantity > db_product.stock_quantity: # type: ignore
            raise HTTPException(status_code=400, detail="Not enough stock for this product")
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item
    else:
        # Add new item to cart
        db_cart_item = CartItemModel(
            ip_address_id=cart_item.ip_address_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item

# @router.post("/", response_model=CartItem, status_code=status.HTTP_201_CREATED)
# def add_to_cart(cart_item: CartItemCreate, 
#                 request: Request,
#                 db: Session = Depends(get_db)
#                 ):

#     # Try to get current user (optional)
    
    
#     current_user = None
    
#     # Get token from Authorization header
#     auth_header = request.headers.get("Authorization")
#     if auth_header and auth_header.startswith("Bearer "):
#         token = auth_header.split(" ")[1]
#         current_user = get_current_user(db, token)
#     else:
#         raise HTTPException(status_code=401, detail="Not authenticated")

#     # Check if product exists
#     db_product = db.query(ProductModel).filter(
#         ProductModel.id == cart_item.product_id).first()
#     if db_product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     # Check if product has enough stock
#     if db_product.stock_quantity < cart_item.quantity: # type: ignore
#         raise HTTPException(status_code=400, detail="Not enough stock for this product")
    
#     # Check if item already in cart
#     db_cart_item = db.query(CartItemModel).filter(
#         CartItemModel.user_id == current_user.id,
#         CartItemModel.product_id == cart_item.product_id
#     ).first()
    
#     if db_cart_item:
#         # Update quantity
#         db_cart_item.quantity += cart_item.quantity # type: ignore
#         if db_cart_item.quantity > db_product.stock_quantity: # type: ignore
#             raise HTTPException(status_code=400, detail="Not enough stock for this product")
#         db.commit()
#         db.refresh(db_cart_item)
#         return db_cart_item
#     else:
#         # Add new item to cart
#         db_cart_item = CartItemModel(
#             user_id=current_user.id,
#             product_id=cart_item.product_id,
#             quantity=cart_item.quantity
#         )
#         db.add(db_cart_item)
#         db.commit()
#         db.refresh(db_cart_item)
#         return db_cart_item


@router.get("/{ip_address_id}", response_model=List[CartItem])
def read_cart(ip_address_id:int, db: Session = Depends(get_db)):
    # Try to get current user (optional)
    # current_user = None
    
    # Get token from Authorization header
    # auth_header = request.headers.get("Authorization")
    # if auth_header and auth_header.startswith("Bearer "):
    #     token = auth_header.split(" ")[1]
    #     current_user = get_current_user(db, token)
    # else:
    #     raise HTTPException(status_code=401, detail="Not authenticated")
    
    cart_items = db.query(CartItemModel).filter(
        CartItemModel.ip_address_id == ip_address_id).order_by(CartItemModel.id).all()
    
    return cart_items

# @router.get("/", response_model=List[CartItem])
# def read_cart(request: Request, db: Session = Depends(get_db)):
#     # Try to get current user (optional)
#     current_user = None
#     
#     # Get token from Authorization header
#     auth_header = request.headers.get("Authorization")
#     if auth_header and auth_header.startswith("Bearer "):
#         token = auth_header.split(" ")[1]
#         current_user = get_current_user(db, token)
#     else:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#     
#     cart_items = db.query(CartItemModel).filter(
#         CartItemModel.user_id == current_user.id).order_by(CartItemModel.id).all()
#     return cart_items

@router.put("/", response_model=CartItem)
def update_cart_item(# cart_item_id: int, 
                     cart_item: CartItemUpdate, 
                     # request: Request,
                     db: Session = Depends(get_db)
                     ):
    # Try to get current user (optional)
    # current_user = None
    
    # Get token from Authorization header
    # auth_header = request.headers.get("Authorization")
    # if auth_header and auth_header.startswith("Bearer "):
    #     token = auth_header.split(" ")[1]
    #     current_user = get_current_user(db, token)
    # else:
    #     raise HTTPException(status_code=401, detail="Not authenticated")
    
    db_cart_item = db.query(CartItemModel).filter(
        CartItemModel.id == cart_item.id,
        CartItemModel.ip_address_id == cart_item.ip_address_id
        #, CartItemModel.user_id == current_user.id
    ).first()

    
    if db_cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found or not authorized")
    
    # Check if product has enough stock
    db_product = db.query(ProductModel).filter(ProductModel.id == db_cart_item.product_id).first()

    if db_product.stock_quantity < cart_item.quantity: # type: ignore
        raise HTTPException(status_code=400, detail="Not enough stock for this product")
    
    db_cart_item.quantity = cart_item.quantity # type: ignore
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item

# @router.put("/{cart_item_id}", response_model=CartItem)
# def update_cart_item(cart_item_id: int, 
#                      cart_item: CartItemUpdate, 
#                      request: Request,
#                      db: Session = Depends(get_db)
#                      ):
#     # Try to get current user (optional)
#     current_user = None
#     
#     # Get token from Authorization header
#     auth_header = request.headers.get("Authorization")
#     if auth_header and auth_header.startswith("Bearer "):
#         token = auth_header.split(" ")[1]
#         current_user = get_current_user(db, token)
#     else:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#     
#     db_cart_item = db.query(CartItemModel).filter(
#         CartItemModel.id == cart_item_id,
#         CartItemModel.user_id == current_user.id
#     ).first()
#     if db_cart_item is None:
#         raise HTTPException(status_code=404, detail="Cart item not found or not authorized")
#     
#     # Check if product has enough stock
#     db_product = db.query(ProductModel).filter(ProductModel.id == db_cart_item.product_id).first()
#     if db_product.stock_quantity < cart_item.quantity: # type: ignore
#         raise HTTPException(status_code=400, detail="Not enough stock for this product")
#     
#     db_cart_item.quantity = cart_item.quantity # type: ignore
#     db.commit()
#     db.refresh(db_cart_item)
#     return db_cart_item

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(cart_item: CartItemDelete,
                     db: Session = Depends(get_db)
                     ):
    # Try to get current user (optional)
    
    # current_user = None
    # 
    # # Get token from Authorization header
    # auth_header = request.headers.get("Authorization")
    # if auth_header and auth_header.startswith("Bearer "):
    #     token = auth_header.split(" ")[1]
    #     current_user = get_current_user(db, token)
    # else:
    #     raise HTTPException(status_code=401, detail="Not authenticated")
    
    db_cart_item = db.query(CartItemModel).filter(
        CartItemModel.id == cart_item.id,
        CartItemModel.ip_address_id == cart_item.ip_address_id
    ).first()
    if db_cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found or not authorized")
    
    db.delete(db_cart_item)
    db.commit()
    return

# @router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
# def remove_from_cart(cart_item_id: int, 
#                      request: Request,
#                      db: Session = Depends(get_db)
#                      ):
#     # Try to get current user (optional)
#     
#     current_user = None
#     
#     # Get token from Authorization header
#     auth_header = request.headers.get("Authorization")
#     if auth_header and auth_header.startswith("Bearer "):
#         token = auth_header.split(" ")[1]
#         current_user = get_current_user(db, token)
#     else:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#     
#     db_cart_item = db.query(CartItemModel).filter(
#         CartItemModel.id == cart_item_id,
#         CartItemModel.user_id == current_user.id
#     ).first()
#     if db_cart_item is None:
#         raise HTTPException(status_code=404, detail="Cart item not found or not authorized")
#     
#     db.delete(db_cart_item)
#     db.commit()
#     return
# 