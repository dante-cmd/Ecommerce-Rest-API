from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from app.database.database import get_db
from app.models.models import UserIP as UserIPModel
from app.models.models import User as UserModel
from app.models.models import IP as IPModel
from app.schemas.schemas import UserIP, UserIPCreate
from sqlalchemy import outerjoin

router = APIRouter()


@router.post("/", response_model=UserIP, status_code=status.HTTP_201_CREATED)
def register_ip_for_user(ip: UserIPCreate, db: Session = Depends(get_db)):
    # Check if ip already exists (only ip is unique)
    db_ip = db.query(UserIPModel).filter(UserIPModel.ip_id == ip.ip_id).first()
    if db_ip:
        raise HTTPException(status_code=400, detail="IP already registered")

    # Create ip
    db_ip = UserIPModel(
        user_id=ip.user_id,
        ip_id=ip.ip_id
    )
    db.add(db_ip)
    db.commit()
    db.refresh(db_ip)
    return db_ip

@router.get("/{ip_id}", response_model=UserIP)
def read_ip(ip_id: int, db: Session = Depends(get_db)):
    db_ip = db.query(UserIPModel).filter(UserIPModel.ip_id == ip_id).first()
    if db_ip is None:
        raise HTTPException(status_code=404, detail="IP not found")
    return db_ip

@router.get("/random", response_model=UserIP)
def get_random_ip(db: Session = Depends(get_db)):
    db_ip = db.query(UserIPModel).order_by(func.newid()).first()
    if db_ip is None:
        raise HTTPException(status_code=404, detail="IP not found")
    return db_ip

@router.get("/user/{user_id}", response_model=UserIP)
def get_ip_by_user(user_id: int, db: Session = Depends(get_db)):
    db_ip = db.query(UserIPModel, UserModel).outerjoin(
        UserModel, UserIPModel.user_id == UserModel.id).all()
    #.filter(UserIPModel.user_id == user_id).first()
    if db_ip is None:
        raise HTTPException(status_code=404, detail="IP not found")
    return db_ip
