import os
import threading
import uvicorn
import httpx
import requests
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from nicegui import ui
from sqlalchemy.orm import Session
from database.database import SessionLocal, get_db
from database.crud.class_mgmt import get_classes_by_trainer_id, create_class_booking
from database.crud.training import get_training_plan_by_id, create_training_plan
from database.crud.user import create_user, get_user_by_email

# 🔹 CONFIGURATION
API_HOST = "127.0.0.1"
API_PORT = 8000
UI_PORT = 8080

# Load environment variables
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID", "your-client-id")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET", "your-client-secret")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "your-auth0-domain")
SECRET_KEY = os.getenv("APP_SECRET_KEY", "your-secret-key-change-this")
AUTH0_CONNECTION = os.getenv("AUTH0_CONNECTION", "Username-Password-Authentication")

# 🔹 Initialize FastAPI for API
api = FastAPI()

# 🔹 CORS & Sessions
api.add_middleware(
    SessionMiddleware, secret_key=SECRET_KEY
)
api.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{API_HOST}:{UI_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Configure OAuth for Auth0
oauth = OAuth()
oauth.register(
    name="auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration',
)

# 🔹 Store user sessions globally
user_sessions = {}


# ✅ AUTH ROUTES
@api.get("/login")
async def login(request: Request):
    redirect_uri = f"http://{API_HOST}:{API_PORT}/callback"
    return await oauth.auth0.authorize_redirect(request, redirect_uri)


@api.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.auth0.authorize_access_token(request)
        user_info = token.get("userinfo")
        if user_info:
            user_id = user_info.get("sub")
            user_sessions[user_id] = dict(user_info)
            request.session["user_id"] = user_id

            # Save user to database
            db_user = get_user_by_email(db, user_info["email"])
            if not db_user:
                user_data = {
                    "email": user_info["email"],
                    "first_name": user_info.get("given_name"),
                    "last_name": user_info.get("family_name"),
                    "user_type": "member",  # Default to member
                }
                create_user(db, user_data)

            return RedirectResponse(url=f"http://{API_HOST}:{UI_PORT}/?user_id={user_id}")
    except Exception as e:
        print(f"Auth0 Callback Error: {e}")
        return RedirectResponse(url=f"http://{API_HOST}:{UI_PORT}/login-failed")


@api.get("/logout")
async def logout(request: Request):
    user_id = request.session.get("user_id")
    if user_id in user_sessions:
        del user_sessions[user_id]
    request.session.pop("user_id", None)

    logout_url = f"https://{AUTH0_DOMAIN}/v2/logout?" \
                 f"client_id={AUTH0_CLIENT_ID}&" \
                 f"returnTo=http://{API_HOST}:{UI_PORT}/"
    return RedirectResponse(url=logout_url)


@api.get("/user")
async def get_user(request: Request):
    user_id = request.session.get("user_id")
    return user_sessions.get(user_id) if user_id else None


# ✅ NICEGUI FRONTEND
@ui.page('/')
def home_page(user_id: str = None):
    ui.query('.nicegui-content').classes('items-center')

    with ui.card().classes('w-96 p-6'):
        ui.label('Welcome to GYMO').classes('text-2xl font-bold text-center mb-4')

        if user_id:
            ui.button('Working Hours', on_click=lambda: ui.navigate.to('/working-hours')).classes('w-full bg-blue-500 text-white mb-2')
            ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('w-full bg-blue-500 text-white mb-2')
            ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('w-full bg-blue-500 text-white mb-2')
            ui.button('Logout', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/logout')).classes('w-full bg-red-500 text-white')
        else:
            ui.label('Please log in to continue').classes('text-center mb-4')
            ui.button('Login with Auth0', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white')


@ui.page('/working-hours')
def working_hours_page():
    ui.query('.nicegui-content').classes('items-center')

    with ui.card().classes('w-96 p-6'):
        ui.label('Working Hours').classes('text-2xl font-bold text-center mb-4')
        ui.label('Monday - Friday: 6:00 AM - 10:00 PM').classes('text-center mb-2')
        ui.label('Saturday - Sunday: 8:00 AM - 8:00 PM').classes('text-center mb-2')
        ui.button('Go Home', on_click=lambda: ui.navigate.to('/')).classes('w-full bg-gray-500 text-white')


# @ui.page('/classes')
# def classes_page():
#     ui.query('.nicegui-content').classes('items-center')

#     with ui.card().classes('w-96 p-6'):
#         ui.label('Classes').classes('text-2xl font-bold text-center mb-4')

#         # Fetch and display classes
#         response = requests.get(f"http://{API_HOST}:{API_PORT}/api/classes")
#         if response.status_code == 200:
#             classes = response.json()
#             for class_ in classes:
#                 ui.label(f"{class_['name']} - {class_['trainer']}").classes('text-center mb-2')
#                 ui.label(f"Date: {class_['date']} | Time: {class_['time']}").classes('text-center mb-2')
#                 if class_['available_slots'] > 0:
#                     ui.button('Book Now', on_click=lambda c=class_: book_class(c['id'])).classes('w-full bg-green-500 text-white mb-2')
#                 else:
#                     ui.label('Class Full').classes('text-center text-red-500 mb-2')
#         else:
#             ui.label('Failed to load classes.').classes('text-center text-red-500 mb-2')

#         ui.button('Go Home', on_click=lambda: ui.navigate.to('/')).classes('w-full bg-gray-500 text-white')


# @ui.page('/training-plans')
# def training_plans_page():
#     ui.query('.nicegui-content').classes('items-center')

#     with ui.card().classes('w-96 p-6'):
#         ui.label('Training Plans').classes('text-2xl font-bold text-center mb-4')

#         # Fetch and display training plans
#         response = requests.get(f"http://{API_HOST}:{API_PORT}/api/training-plans")
#         if response.status_code == 200:
#             plans = response.json()
#             for plan in plans:
#                 ui.label(f"{plan['title']} - {plan['goal']}").classes('text-center mb-2')
#                 ui.label(f"Duration: {plan['duration']} weeks").classes('text-center mb-2')
#                 ui.button('Save Plan', on_click=lambda p=plan: save_training_plan(p['id'])).classes('w-full bg-blue-500 text-white mb-2')
#         else:
#             ui.label('Failed to load training plans.').classes('text-center text-red-500 mb-2')

#         ui.button('Go Home', on_click=lambda: ui.navigate.to('/')).classes('w-full bg-gray-500 text-white')


# ✅ RUN SERVERS
def run_api():
    user_sessions.clear()
    uvicorn.run(api, host=API_HOST, port=API_PORT)


def run_ui():
    ui.run(port=UI_PORT, title="GYMO - Gym Manager", favicon="💪")


if __name__ in {"__main__", "__mp_main__"}:
    threading.Thread(target=run_api, daemon=True).start()
    run_ui()