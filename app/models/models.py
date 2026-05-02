from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.database.database import Base


class IPAddress(Base):
    __tablename__ = "ip_addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user_ip = relationship("UserIPAddress", back_populates="ip_address")
    interactions = relationship("Interaction", back_populates="ip_address")
    cart_items = relationship("CartItem", back_populates="ip_address")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    full_name = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user_ip = relationship("UserIPAddress", back_populates="user")
    order = relationship("Order", back_populates="user")
    # cart_items = relationship("CartItem", back_populates="user")


class UserIPAddress(Base):
    __tablename__ = "user_ip_addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address_id = Column(Integer, ForeignKey("ip_addresses.id"), unique=True)  # Each IPAddress can only be associated with one user
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    ip_address = relationship("IPAddress", back_populates="user_ip")
    user = relationship("User", back_populates="user_ip")
    

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), index=True)
    description = Column(Text)
    price = Column(Float)
    category = Column(String(500), index=True)
    image_url = Column(String(500))
    stock_quantity = Column(Integer)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    # interactions = relationship("Interaction", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float)
    status = Column(String(50), default="pending")  # pending, confirmed, shipped, delivered
    payment_method = Column(String(50))  # credit_card, debit_card, paypal, etc.
    bank = Column(String(100))  # Bank associated with the payment method
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="order")
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)  # Price at the time of purchase
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address_id = Column(Integer, ForeignKey("ip_addresses.id"))  
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    
    # Relationships
    ip_address = relationship("IPAddress", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address_id = Column(Integer, ForeignKey("ip_addresses.id"))
    interaction_type = Column(String(50))  # view, click, add_to_cart, purchase, out_of_stock
    interaction_metadata = Column(Text, nullable=True, default=None)  # Additional information about the interaction
    created_at = Column(DateTime, server_default=func.now())
    # product_id = Column(Integer, ForeignKey("products.id"))
    
    # ip_address = Column(String(45), nullable=True)  # For tracking anonymous users by IPAddress (IPv6 max length)
    
    # Relationships
    # user = relationship("User", back_populates="interactions")
    ip_address = relationship("IPAddress", back_populates="interactions")
    # product = relationship("Product", back_populates="interactions")
