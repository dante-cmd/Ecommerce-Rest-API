from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# --------------- UserIP schemas -----------------
class UserIPAddressBase(BaseModel):
    user_id: int
    ip_address_id: int

class UserIPAddressCreate(UserIPAddressBase):
    pass

class UserIPAddress(UserIPAddressBase):
    pass

# -------------- End IP schemas --------------

# --------------- IP schemas -----------------
class IPBase(BaseModel):
    ip_address: str

class IPAddressCreate(IPBase):
    pass

class IPAddress(IPBase):
    id: int
    pass

# -------------- End IP schemas --------------

# -------------- User schemas ----------------
class UserBase(BaseModel):
    email: str
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str
    created_at: Optional[datetime] = None

class UserRecovery(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ----------- End User schemas --------------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int

# ----------- Product schemas --------------
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image_url: Optional[str] = None
    stock_quantity: int
    is_available: bool = True

class ProductCreate(ProductBase):
    created_at: datetime

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --------- End Product schemas ------------


# ------------- Order schemas ------------
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    price: float
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    pass

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    payment_method: Optional[str] = "credit_card"
    bank: Optional[str] = "Visa"
    # created_at: datetime

class OrderUpdate(BaseModel):
    status: str
    # updated_at: datetime

class Order(OrderBase):
    id: int
    user_id: int
    total_amount: float
    status: str
    payment_method: Optional[str]
    bank: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItem] = []
    
    class Config:
        from_attributes = True
# --------- End Order schemas ------------

# Cart schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItem(CartItemBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True


# User Interaction schemas

class InteractionBase(BaseModel):
    ip_address_id: int
    # product_id: int
    interaction_type: str
    interaction_metadata: Optional[str]=None
    # ip_address: Optional[str] = None

class InteractionCreate(InteractionBase):
    pass
    # timestamp: datetime

class Interaction(InteractionBase):
    id: int
    # timestamp: datetime
    
    class Config:
        from_attributes = True