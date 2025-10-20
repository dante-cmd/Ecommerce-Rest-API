import pymssql
import os

# Configuración de conexión
SERVER = "sqlserver"
DATABASE = "master"  # Base de datos master para crear la nueva base de datos
USERNAME = "sa"
PASSWORD = "YourStrong@Passw0rd"
AGAIN = True 
# Create the database again (True, only for dev)

def create_database():
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
        if AGAIN:
            cursor.execute("DROP DATABASE IF EXISTS ecommerce_db")
            print("Base de datos 'ecommerce_db' Eliminadas exitosamente")
            cursor.execute("CREATE DATABASE ecommerce_db")
            print("Base de datos 'ecommerce_db' creada exitosamente")
        else:
        
            # Verificar si la base de datos existe
            cursor.execute("SELECT name FROM sys.databases WHERE name = 'ecommerce_db'")
            result = cursor.fetchone()
            
            if not result:
                # Crear la base de datos si no existe
                cursor.execute("CREATE DATABASE ecommerce_db")
            
            print("Base de datos 'ecommerce_db' creada exitosamente")
        
        # Cerrar la conexión
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")

if __name__ == "__main__":
    create_database()