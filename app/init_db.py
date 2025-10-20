# Initialize database with sample data
from app.database.database import SessionLocal, engine
from app.models.models import Base, User, Product
from app.core.security import get_password_hash
import time
import pandas as pd

def init_db():
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = SessionLocal()
    
    try:        
        # Check if we already have products
        product_count = db.query(Product).count()
        if product_count == 0:
            products = pd.read_csv('app/products.csv')
            for product in products.itertuples(index=False):
                item_product = Product(
                        name=product.name,
                        description=product.description,
                        price=product.price,
                        category=product.category,
                        image_url = product.image_url,
                        stock_quantity=product.stock_quantity,
                        is_available=True
                    )
                db.add(item_product)
            print("Added sample products to database")

        # Check if we already have users
        user_count = db.query(User).count()
        if user_count == 0:
            users = pd.read_csv('app/customers.csv')
            for user in users.itertuples(index=False):
                item_user = User(
                    email=user.email,
                    username=user.username,
                    hashed_password=get_password_hash(user.password),
                    is_active=True,
                    is_admin=False
                )
                db.add(item_user)

            # Create sample users
            admin_user = User(
                    email="admin@example.com",
                    username="admin",
                    hashed_password=get_password_hash("adminpassword"),
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