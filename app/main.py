from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import ip_address, products, user_ip_address, users, orders, cart, interactions
# from app.database import database
from app.create_db import drop_if_exists_and_create_db
from app.init_db import init_db
# from app.models import models
import time

# Wait for database to be ready
time.sleep(10)

# Create database
try:
    drop_if_exists_and_create_db()
    print("Database created successfully")
except Exception as e:
    print(f"Error creating database: {e}")

# Create tables
# try:
#     models.Base.metadata.create_all(bind=database.engine)
#     print("Database tables created successfully")
# except Exception as e:
#     print(f"Error creating database tables: {e}")

# Initialize with sample data
try:
    init_db()
    print("Database initialized with sample data")
except Exception as e:
    print(f"Error initializing database: {e}")

app = FastAPI(
    title="E-commerce API",
    description="A simple e-commerce API built with FastAPI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers

app.include_router(ip_address.router, prefix="/api/ip_address", tags=["ip_address"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(user_ip_address.router, prefix="/api/user_ip_address", tags=["user_ip_address"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(cart.router, prefix="/api/cart", tags=["cart"])
app.include_router(interactions.router, prefix="/api/interactions", tags=["interactions"])

@app.get("/")
async def root():
    return {"message": "Welcome to the E-commerce API"}