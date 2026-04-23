from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from app.database.database import get_db
from app.models.models import User as UserModel
from app.schemas.schemas import User, UserCreate, Token, UserRecovery
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class TokenRequest(BaseModel):
    email: str
    password: str

class TokenRequestWithoutPassword(BaseModel):
    email: str


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 
    # Check if user already exists (only email is unique)
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user
    db_user = UserModel(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(UserModel).order_by(UserModel.id).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/email/{email}", response_model=User)
def read_user_by_email(email: str, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == email).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/token")
def login_for_access_token(token_request: TokenRequest, db: Session = Depends(get_db)):
    # = Form(...)
    user = db.query(UserModel).filter(UserModel.email == token_request.email).first()
    if not user or not verify_password(token_request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token_without_password")
def login_for_access_token_without_password(token_request: TokenRequestWithoutPassword, db: Session = Depends(get_db)):
    # = Form(...)
    user = db.query(UserModel).filter(UserModel.email == token_request.email).first()
    if not user: 
        # or not verify_password(token_request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}