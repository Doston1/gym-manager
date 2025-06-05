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
    pool_size=10,  # Adjust pool size as needed
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT,
    auth_plugin='mysql_native_password' # Or caching_sha2_password depending on your MySQL version
)

# Dependency to get DB connection and cursor from the pool
def get_db_cursor():
    connection = None
    cursor = None
    try:
        connection = db_pool.get_connection()
        # dictionary=True returns rows as dictionaries {column_name: value}
        cursor = connection.cursor(dictionary=True) 
        yield connection, cursor
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Dependency to get DB connection (for transactions spanning multiple cursor operations)
def get_db_connection():
    connection = None
    try:
        connection = db_pool.get_connection()
        yield connection
    finally:
        if connection and connection.is_connected():
            connection.close()


# Test function to check database connection (optional)
def test_db_connection():
    try:
        conn, cursor = next(get_db_cursor()) # Get a connection and cursor
        if conn.is_connected():
            print("Successfully connected to the database.")
            cursor.execute("SELECT DATABASE();")
            db_name_row = cursor.fetchone()
            if db_name_row:
                print(f"Current database: {db_name_row['DATABASE()']}")
        else:
            print("Failed to connect to the database.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        # get_db_cursor handles closing
        pass

if __name__ == "__main__":
    test_db_connection()