from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database.database import get_db
from app.models.models import Product as ProductModel
from app.schemas.schemas import Product, ProductCreate, ProductUpdate

router = APIRouter()

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# @router.get("/", response_model=List[Product])
# def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     products = db.query(ProductModel).order_by(ProductModel.id).offset(skip).limit(limit).all()
#     return products

@router.get("/", response_model=List[Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Use dialect-appropriate random ordering
    dialect_name = db.get_bind().dialect.name
    if dialect_name == "mssql":
        order_by = func.newid()
    elif dialect_name == "postgresql":
        order_by = func.random()
    else:
        order_by = func.random()
    products = db.query(
        ProductModel).order_by(
            order_by).offset(skip).limit(limit).all()
    return products

# @router.get("/{n_products}", response_model=List[Product])
# def get_random_product(n_products: int, db: Session = Depends(get_db)):
#     db_product = db.query(ProductModel).order_by(func.newid()).limit(n_products).all()
#     if db_product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return db_product


# @router.get("/availability/{product_id}/{quantity}", response_model=List[Product])
# def check_availability(product_id: int, quantity: int, db: Session = Depends(get_db)):
#     products = db.query(ProductModel).filter(
#         ProductModel.id == product_id, ProductModel.stock_quantity >= quantity).all()
#     #.order_by(ProductModel.id).offset(skip).limit(limit).all()
#     return products



@router.get("/{product_id}", response_model=Product)
def read_product(product_id: int, quantity: int=0, db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).filter(
        ProductModel.id == product_id , ProductModel.stock_quantity >= quantity).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return