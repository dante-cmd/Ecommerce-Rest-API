from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import quote_plus

# Configuración para MSSQL
# En producción, deberías usar variables de entorno para las credenciales
# localhost
SERVER = os.getenv("DB_SERVER", "sqlserver")
DATABASE = os.getenv("DB_DATABASE", "ecommerce_db")
USERNAME = os.getenv("DB_USERNAME", "sa")
PASSWORD = os.getenv("DB_PASSWORD", "YourStrong@Passw0rd")

# Usar pymssql connection (sin ODBC)
connection_string = f"mssql+pymssql://{USERNAME}:{quote_plus(PASSWORD)}@{SERVER}:1433/{DATABASE}"

SQLALCHEMY_DATABASE_URL = connection_string

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()