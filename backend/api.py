import os
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.auth import setup_auth_routes
from starlette.middleware.sessions import SessionMiddleware

# Load environment variables
API_HOST = os.getenv("API_HOST", "127.0.0.1") # Make sure these are loaded, e.g. from .env
API_PORT = int(os.getenv("API_PORT", 8000))
SECRET_KEY = os.getenv("APP_SECRET_KEY", "your-very-secret-key-for-session") # Ensure this is strong

# Initialize FastAPI
api = FastAPI()

api.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)
# Middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{API_HOST}:8080", f"http://localhost:8080"], # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
setup_auth_routes(api)

@api.get("/testos")
def test_os_route(): # Renamed to avoid conflict if test_os is imported elsewhere
    return {"message": "OS test route is alive"}

# API Routes (import from routes folder)
from backend.routes import users, classes, custom_requests, facilities, finance, training_blueprints, training_execution, scheduling, notifications 
# Add other route modules here as they are refactored/created
# e.g., from backend.routes import facilities, memberships, analytics_routes, etc.

api.include_router(users.router) 
api.include_router(classes.router)
api.include_router(custom_requests.router)
api.include_router(facilities.router)
api.include_router(finance.router)
api.include_router(training_blueprints.router)
api.include_router(training_blueprints.training_plans_router)  # Additional router for /training-plans paths
api.include_router(training_execution.router)
api.include_router(training_execution.training_router)  # Additional router for /training paths
api.include_router(scheduling.router)
api.include_router(notifications.router)

# Run API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api:api", host=API_HOST, port=API_PORT, reload=True) # Added reload=True for dev