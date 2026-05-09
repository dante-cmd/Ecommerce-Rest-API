from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ReviewBase(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    title: Optional[str] = None
    content: str
    images: Optional[List[str]] = []


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    content: Optional[str] = None
    images: Optional[List[str]] = None


class Review(ReviewBase):
    id: str
    user_id: int
    helpful_votes: int = 0
    verified_purchase: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
