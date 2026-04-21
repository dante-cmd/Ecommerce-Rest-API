from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from app.database.database import get_db
from app.models.models import UserIPAddress as UserIPModel
from app.schemas.schemas import UserIPAddress, UserIPAddressCreate
from sqlalchemy import outerjoin

router = APIRouter()


@router.post("/", response_model=UserIPAddress, status_code=status.HTTP_201_CREATED)
def register_ip_for_user(user_ip_address: UserIPAddressCreate, db: Session = Depends(get_db)):
    # Check if ip already exists (only ip is unique)
    db_ip = db.query(UserIPModel).filter(
        UserIPModel.ip_address_id == user_ip_address.ip_address_id).first()
    if db_ip:
        raise HTTPException(status_code=400, detail="IP already registered")

    # Create ip
    db_ip = UserIPModel(
        user_id=user_ip_address.user_id,
        ip_address_id=user_ip_address.ip_address_id
    )
    db.add(db_ip)
    db.commit()
    db.refresh(db_ip)
    return db_ip

@router.get("/{ip_id}", response_model=UserIPAddress)
def read_ip(ip_id: int, db: Session = Depends(get_db)):
    db_ip = db.query(UserIPModel).filter(UserIPModel.ip_id == ip_id).first()
    if db_ip is None:
        raise HTTPException(status_code=404, detail="IP not found")
    return db_ip

@router.get("/random", response_model=UserIPAddress)
def get_random_ip(db: Session = Depends(get_db)):
    db_ip = db.query(UserIPModel).order_by(func.newid()).first()
    if db_ip is None:
        raise HTTPException(status_code=404, detail="IP not found")
    return db_ip

