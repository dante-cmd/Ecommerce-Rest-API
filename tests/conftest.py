"""
Pytest configuration file for the ecommerce API tests.

This file is automatically discovered by pytest and runs before any tests.
It adds the project root to sys.path so imports work correctly.
"""

import sys
from pathlib import Path
import pytest
import os

# Set environment variable to skip database initialization during tests
os.environ["SKIP_DB_INIT"] = "true"

# Add the project root to sys.path so imports like 'from app...' work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Remove stale test database if it exists
TEST_DB_PATH = Path(__file__).parent.parent / "test_ecommerce.db"
if TEST_DB_PATH.exists():
    try:
        TEST_DB_PATH.unlink()
    except Exception:
        pass


@pytest.fixture(scope="session")
def client():
    """Create a TestClient for the app."""
    from fastapi.testclient import TestClient
    from app.database.database import Base, get_db
    from app.main import app
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Setup test database
    SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_ecommerce.db"
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Drop all tables and recreate fresh
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    
    yield client
    
    # Cleanup after session
    Base.metadata.drop_all(bind=engine)



