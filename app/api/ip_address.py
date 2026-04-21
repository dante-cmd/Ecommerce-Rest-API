from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from app.database.database import get_db
from app.models.models import IPAddress as IPModel
from app.schemas.schemas import IPAddress, IPAddressCreate

router = APIRouter()


@router.post("/", response_model=IPAddress, status_code=status.HTTP_201_CREATED)
def register_ip(ip_address: IPAddressCreate, db: Session = Depends(get_db)):
    # Check if ip already exists (only ip is unique)
    db_ip = db.query(IPModel).filter(IPModel.ip_address == ip_address.ip_address).first()
    if db_ip:
        raise HTTPException(status_code=400, detail="IP already registered")

    # Create ip
    db_ip = IPModel(ip_address = ip_address.ip_address)
    db.add(db_ip)
    db.commit()
    db.refresh(db_ip)
    return db_ip

@router.get("/{ip_address}", response_model=IPAddress)
def read_ip(ip_address: str, db: Session = Depends(get_db)):
    db_ip = db.query(IPModel).filter(IPModel.ip_address == ip_address).first()
    if db_ip is None:
        raise HTTPException(status_code=404, detail="IP not found")
    return db_ip

@router.get("/", response_model=List[IPModel])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    #  func.newid() is a random number generator. 
    # This is SQL Server-specific and won't work on PostgreSQL/MySQL.
    ip_addresses = db.query(IPModel).order_by(func.newid()).offset(skip).limit(limit).all()
    # ip_addresses = db.query(IPModel).order_by(IPModel.id).offset(skip).limit(limit).all()
    return ip_addresses

# @router.get("/random", response_model=IPAddress)
# def get_random_ip(db: Session = Depends(get_db)):
#     db_ip = db.query(IPModel).order_by(func.newid()).first()
#     if db_ip is None:
#         raise HTTPException(status_code=404, detail="IP not found")
#     return db_ip