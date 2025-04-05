import os
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
# from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from backend.auth import setup_auth_routes
from starlette.middleware.sessions import SessionMiddleware


# Load environment variables
API_HOST = "127.0.0.1"
API_PORT = 8000
SECRET_KEY = os.getenv("APP_SECRET_KEY", "your-secret-key")

# Initialize FastAPI
api = FastAPI()

api.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY  # a strong random string
)
# Middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{API_HOST}:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication (moved to backend/auth.py)
setup_auth_routes(api)

@api.get("/testos")
def test_os():
    return {"message": "OS test route is alive"}

# API Routes (import from routes folder)
from backend.routes import users, classes, training
api.include_router(users.router) 
api.include_router(classes.router)
api.include_router(training.router)


# Run API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host=API_HOST, port=API_PORT)
