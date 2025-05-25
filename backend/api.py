# backend/api.py
import os
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from authlib.integrations.starlette_client import OAuth
from backend.auth import setup_auth_routes
from starlette.middleware.sessions import SessionMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.scheduling.scheduler import run_initial_scheduling, run_final_scheduling_adjustments

# Load environment variables
API_HOST = os.getenv("API_HOST", "127.0.0.1") # Added default
API_PORT = int(os.getenv("API_PORT", "8000")) # Added default and int conversion
SECRET_KEY = os.getenv("APP_SECRET_KEY", "your-secret-key-please-change") # Stronger default

# Initialize FastAPI
api = FastAPI()

# Initialize Scheduler
scheduler = AsyncIOScheduler()

api.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)
api.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{API_HOST}:8080", f"http://localhost:8080"], # Allow localhost for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_auth_routes(api)

@api.on_event("startup")
async def startup_event():
    # Schedule jobs
    # Note: For cron, day_of_week '4' is Friday, '5' is Saturday if Monday is 0.
    # APScheduler: fri = 4, sat = 5 (if week starts on Mon) or fri, sat
    scheduler.add_job(run_initial_scheduling, 'cron', day_of_week='fri', hour=0, minute=1, timezone='UTC') # UTC recommended
    scheduler.add_job(run_final_scheduling_adjustments, 'cron', day_of_week='sat', hour=0, minute=1, timezone='UTC')
    scheduler.start()
    print("APScheduler started with jobs.")

@api.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print("APScheduler shutdown.")


@api.get("/testos")
def test_os():
    return {"message": "OS test route is alive"}

from backend.routes import users, classes, training
api.include_router(users.router, prefix="/api") # Added /api prefix
api.include_router(classes.router, prefix="/api") # Added /api prefix
api.include_router(training.router, prefix="/api") # Added /api prefix

# Main run block for direct execution (optional, usually Uvicorn handles this)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host=API_HOST, port=API_PORT)



# ----------------------------------------
# import os
# from fastapi import FastAPI, Request, Depends
# from fastapi.middleware.cors import CORSMiddleware
# # from starlette.middleware.sessions import SessionMiddleware
# from authlib.integrations.starlette_client import OAuth
# from backend.auth import setup_auth_routes
# from starlette.middleware.sessions import SessionMiddleware


# # Load environment variables
# API_HOST = "127.0.0.1"
# API_PORT = 8000
# SECRET_KEY = os.getenv("APP_SECRET_KEY", "your-secret-key")

# # Initialize FastAPI
# api = FastAPI()

# api.add_middleware(
#     SessionMiddleware,
#     secret_key=SECRET_KEY  # a strong random string
# )
# # Middleware
# api.add_middleware(
#     CORSMiddleware,
#     allow_origins=[f"http://{API_HOST}:8080"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Authentication (moved to backend/auth.py)
# setup_auth_routes(api)

# @api.get("/testos")
# def test_os():
#     return {"message": "OS test route is alive"}

# # API Routes (import from routes folder)
# from backend.routes import users, classes, training
# api.include_router(users.router) 
# api.include_router(classes.router)
# api.include_router(training.router)


# # Run API
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(api, host=API_HOST, port=API_PORT)
