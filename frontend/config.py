# filepath: c:\Users\ASUS\Desktop\SemesterProject\frontend\config.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if applicable)
load_dotenv()

# Define environment variables
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = os.getenv("API_PORT", "8000")
UI_PORT = os.getenv("UI_PORT", "8080")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID", "your-client-id")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET", "your-client-secret")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "your-auth0-domain")