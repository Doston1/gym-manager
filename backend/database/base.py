import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database connection details from environment variables
DB_HOST = os.getenv('MYSQL_HOST')
DB_USER = os.getenv('MYSQL_USER')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD')
DB_NAME = os.getenv('MYSQL_DATABASE')
DB_PORT = os.getenv('MYSQL_PORT', 3306) # Default MySQL port

# Create a connection pool
db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,  # Adjust pool size as needed
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT,
    auth_plugin='mysql_native_password' # Or caching_sha2_password depending on your MySQL version
)

# Dependency to get DB connection from the pool
def get_db():
    try:
        connection = db_pool.get_connection()
        yield connection
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

# Test function to check database connection (optional)
def test_db_connection():
    try:
        conn = get_db().__next__() # Get a connection
        if conn.is_connected():
            print("Successfully connected to the database.")
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print(f"Current database: {db_name[0]}")
            cursor.close()
        else:
            print("Failed to connect to the database.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    test_db_connection()