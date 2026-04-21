import pymssql
import os

# Configuración de conexión
SERVER = "sqlserver"
DATABASE = "master"  # Base de datos master para crear la nueva base de datos
USERNAME = "sa"
PASSWORD = "YourStrong@Passw0rd"
AGAIN = True 
NAME_DB = "ecommerce_db"
# Create the database again (True, only for dev)

def drop_if_exists_and_create_db():
    try:
        # Usar pymssql
        conn = pymssql.connect(
            server=SERVER,
            user=USERNAME,
            password=PASSWORD,
            database=DATABASE
        )
        
        conn.autocommit(True)
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {NAME_DB}")
        print(f"Base de datos '{NAME_DB}' Eliminadas exitosamente")
        cursor.execute(f"CREATE DATABASE {NAME_DB}")
        print(f"Base de datos '{NAME_DB}' creada exitosamente")
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")

if __name__ == "__main__":
    drop_if_exists_and_create_db()