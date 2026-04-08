from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from app.database.database import get_db
from app.models.models import IP as IPModel
from app.schemas.schemas import IP, IPCreate

router = APIRouter()


@router.post("/", response_model=IP, status_code=status.HTTP_201_CREATED)
def register_ip(ip: IPCreate, db: Session = Depends(get_db)):
    # Check if ip already exists (only ip is unique)
    db_ip = db.query(IPModel).filter(IPModel.ip == ip.ip).first()
    if db_ip:
        raise HTTPException(status_code=400, detail="IP already registered")

    # Create ip
    db_ip = IPModel(ip = ip.ip)
    db.add(db_ip)
    db.commit()
    db.refresh(db_ip)
    return db_ip


@router.get("/random", response_model=IP)
def get_random_ip(db: Session = Depends(get_db)):
    db_ip = db.query(IPModel).order_by(func.newid()).first()
    if db_ip is None:
        raise HTTPException(status_code=404, detail="IP not found")
    return db_ip

@router.get("/{ip}", response_model=IP)
def read_ip(ip: str, db: Session = Depends(get_db)):
    db_ip = db.query(IPModel).filter(IPModel.ip == ip).first()
    if db_ip is None:
        raise HTTPException(status_code=404, detail="IP not found")
    return db_ip