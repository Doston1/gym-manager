import os
import threading
import uvicorn
import httpx
import requests
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from nicegui import ui
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal, User, get_db

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
            db_user = db.query(User).filter(User.email == user_info["email"]).first()
            if not db_user:
                db_user = User(
                    email=user_info["email"],
                    first_name=user_info.get("given_name"),
                    family_name=user_info.get("family_name"),
                    birth_date=user_info.get("birthdate"),
                    sex=user_info.get("gender"),
                    user_type=3  # Default to member

                )
                db.add(db_user)
                db.commit()
                db.refresh(db_user)

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


@api.get("/check-session")
async def check_session(user_id: str):
    return user_sessions.get(user_id) if user_id in user_sessions else {"error": "User not found"}


# ✅ NICEGUI FRONTEND
@ui.page('/')
def home_page(user_id: str = None):
    ui.query('.nicegui-content').classes('items-center')

    with ui.card().classes('w-96 p-6'):
        ui.label('Welcome to GYMO').classes('text-2xl font-bold text-center mb-4')

        if user_id:
            # 🔹 Fetch session status
            response = requests.get(f"http://{API_HOST}:{API_PORT}/check-session?user_id={user_id}")
            if response.status_code == 200 and "error" not in response.json():
                user = response.json()
                ui.label(f'Hello, {user.get("name", "User")}!').classes('text-lg text-center mb-2')
                ui.label(f'Email: {user.get("email", "No email")}').classes('text-sm text-center mb-4')
                # ui.button('Protected Page', on_click=lambda: ui.navigate.to(f'/protected?user_id{user_id}')).classes('w-full bg-green-500 text-white mb-2')
                ui.button('Personal Area', on_click=lambda: ui.navigate.to(f'/personal-area?user_id={user_id}')).classes('w-full bg-blue-500 text-white mb-2')
                ui.button('Classes', on_click=lambda: ui.navigate.to(f'/classes?user_id={user_id}')).classes('w-full bg-blue-500 text-white mb-2')
                ui.button('Training Plans', on_click=lambda: ui.navigate(f'/training-plans?user_id={user_id}')).classes('w-full bg-blue-500 text-white mb-2')
                ui.button('Logout', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/logout')).classes('w-full bg-red-500 text-white')
            else:
                ui.label('Session expired. Please log in again.').classes('text-center mb-4')
                ui.button('Login with Auth0', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white')
        else:
            ui.label('Please log in to continue').classes('text-center mb-4')
            ui.button('Login with Auth0', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white')


@ui.page('/login-failed')
def login_failed():
    ui.query('.nicegui-content').classes('items-center')
    with ui.card().classes('w-96 p-6'): 
        ui.label('Login Failed').classes('text-2xl font-bold text-center mb-4 text-red-500')
        ui.label('There was a problem authenticating your account.').classes('text-center mb-4')
        ui.button('Try Again', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white mb-2')
        ui.button('Go Home', on_click=lambda: ui.navigate('/')).classes('w-full bg-gray-500 text-white')


@ui.page('/protected')
def protected_page(user_id: str = None):
    ui.query('.nicegui-content').classes('items-center')

    if not user_id:
        ui.navigate('/')
        return

    response = requests.get(f"http://{API_HOST}:{API_PORT}/check-session?user_id={user_id}")
    if response.status_code != 200 or "error" in response.json():
        ui.navigate('/')
        return

    user = response.json()
    with ui.card().classes('w-96 p-6'):
        ui.label('Protected Page').classes('text-2xl font-bold text-center mb-4')
        ui.label(f'Welcome, {user.get("name", "User")}!').classes('text-lg text-center mb-4')
        ui.label('This page is only visible to authenticated users.').classes('text-center mb-4')
        ui.button('Go Home', on_click=lambda: ui.navigate(f'/?user_id={user_id}')).classes('w-full bg-blue-500 text-white')


@ui.page('/signup')
def signup_page():
    ui.query('.nicegui-content').classes('items-center')

    with ui.card().classes('w-96 p-6'):
        ui.label('Create Account').classes('text-2xl font-bold text-center mb-4')

        email_input = ui.input(label='Email', type='email').classes('w-full mb-4')
        password_input = ui.input(label='Password', type='password').classes('w-full mb-4')
        gender_input = ui.select(['Male', 'Female', 'Other'], value='Male').classes('w-full mb-4')
        birthdate_input = ui.input(label='Birthdate', type='date').classes('w-full mb-4')

        def submit():
            payload = {
                "client_id": AUTH0_CLIENT_ID,
                "email": email_input.value,
                "password": password_input.value,
                "connection": AUTH0_CONNECTION,
                "user_metadata": {
                    "gender": gender_input.value,
                    "birthdate": birthdate_input.value,
                    "type": 3 # Default to member
                }
            }

            response = requests.post(f"https://{AUTH0_DOMAIN}/dbconnections/signup", json=payload)

            if response.status_code == 200:
                ui.notify('Signup successful! Please log in.', type='positive')
                ui.navigate('/login')
            else:
                ui.notify(f"Error: {response.json().get('error', 'Signup failed')}", type='negative')

        ui.button('Sign Up', on_click=submit).classes('w-full bg-blue-500 text-white')



# ✅ RUN SERVERS
def run_api():
    # Clear session cookies on server start
    user_sessions.clear()
    uvicorn.run(api, host=API_HOST, port=API_PORT)


def run_ui():
    ui.run(port=UI_PORT, title="GYMO - Auth0 Authentication", favicon="💪")


# if __name__ in {"__main__", "__mp_main__"}:
#     threading.Thread(target=run_api, daemon=True).start()
#     run_ui()
