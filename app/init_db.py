# Initialize database with sample data
from app.database.database import SessionLocal, engine
from app.models.models import Base, User, Product, IPAddress, UserIPAddress
from app.core.security import get_password_hash
import time
from faker import Faker
import pandas as pd
# import random
import numpy as np


fake = Faker()
# Quantity of IP addresses to create

def init_db():
    # Crear todas las tablas
    """
    Initialize database with sample data.

    Creates all tables in the database and populates them with sample data.
    Sample data includes products from a CSV file, users generated using Faker and IP addresses.
    Also creates a sample admin user.

    :return: None
    :raises: Exception: If there is an error initializing the database
    """
    Base.metadata.create_all(bind=engine)
    N_IP_ADDRESSES = 500
    DEFAULT_PASSWORD = "Password123!"
    ADMIN_PASSWORD = "adminpassword"


    # Create a session
    db = SessionLocal()
    
    try:
        # Load products from CSV and add to database
        products = pd.read_csv('app/products.csv')
        
        for product in products.itertuples(index=False):
            assert isinstance(product.stock_quantity, (int, float)), f"Stock quantity for {product.name} is not a number: {product.stock_quantity}"
            item_product = Product(
                        name=product.name,
                        description=product.description,
                        price=product.price,
                        category=product.category,
                        image_url = product.image_url,
                        stock_quantity= max(20, product.stock_quantity),
                        is_available=True
                    )
            db.add(item_product)

        print("Added sample products to database")
    
        # Load users using Faker
        while True:

            db_ip_address = IPAddress(
                ip_address = fake.unique.ipv4()
            )
            
            db.add(db_ip_address)
            db.commit()
            db.refresh(db_ip_address)
            
            N_IP_ADDRESSES -= 1
            if N_IP_ADDRESSES <= 0:
                break
            
            # Randomly decide if this user will have an associated IP address (simulate some users without IPs)
            has_a_user = np.random.choice([True, False], p=[0.2, 0.8], replace=False)

            if has_a_user:
                db_user = User(
                    email = fake.unique.email(),
                    username = fake.unique.user_name(),
                    hashed_password=get_password_hash(DEFAULT_PASSWORD),
                    is_active=True,
                    is_admin=False,
                    full_name = fake.unique.name()
                    )
                db.add(db_user)
                db.commit()
                db.refresh(db_user)

                # Associate user with a IP address 
                user_ip_address = UserIPAddress(
                    user_id = db_user.id,
                    ip_address_id = db_ip_address.id
                    )
                db.add(user_ip_address)
                db.commit()

        print("Added sample users to database")

        # Create a sample of admin user
        admin_user = User(
                    email="admin@example.com",
                    username="admin",
                    hashed_password=get_password_hash(ADMIN_PASSWORD),
                    is_active=True,
                    is_admin=True)
        db.add(admin_user)
            
        print("Added sample users to database")

        # Commit changes
        db.commit()
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()