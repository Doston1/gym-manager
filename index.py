import os
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from nicegui import ui
import uvicorn
import threading


# Configuration
API_HOST = "127.0.0.1"
API_PORT = 8000
UI_PORT = 8080

# Initialize FastAPI for the API
api = FastAPI()

# Configure session middleware
api.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("APP_SECRET_KEY", "your-secret-key-change-this")
)

# Configure Auth0
oauth = OAuth()
oauth.register(
    name="auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# Global storage for user sessions
user_sessions = {}

# Auth routes
@api.get("/login")
async def login(request: Request):
    # Make callback URL go to the API server
    redirect_uri = f"http://{API_HOST}:{API_PORT}/callback"
    return await oauth.auth0.authorize_redirect(request, redirect_uri)

@api.get("/callback")
async def callback(request: Request):
    try:
        token = await oauth.auth0.authorize_access_token(request)
        user = token.get("userinfo")
        if user:
            user_id = user.get("sub")
            user_sessions[user_id] = dict(user)
            request.session["user_id"] = user_id
            
            # Redirect to UI server with session ID
            return RedirectResponse(url=f"http://{API_HOST}:{UI_PORT}/?user_id={user_id}")
    except Exception as e:
        print(f"Error during callback: {e}")
        return RedirectResponse(url=f"http://{API_HOST}:{UI_PORT}/login-failed")

@api.get("/logout")
async def logout(request: Request):
    user_id = request.session.get("user_id")
    if user_id and user_id in user_sessions:
        del user_sessions[user_id]
    request.session.pop("user_id", None)
    
    # Construct Auth0 logout URL
    domain = os.getenv("AUTH0_DOMAIN")
    client_id = os.getenv("AUTH0_CLIENT_ID")
    return_to = f"http://{API_HOST}:{UI_PORT}/"
    
    return RedirectResponse(
        url=f"https://{domain}/v2/logout?"
            f"client_id={client_id}&"
            f"returnTo={return_to}"
    )

@api.get("/user")
async def get_user(request: Request):
    user_id = request.session.get("user_id")
    if user_id:
        return user_sessions.get(user_id)
    return None

@api.get("/check-session")
async def check_session(user_id: str):
    if user_id in user_sessions:
        return user_sessions[user_id]
    return {"error": "User not found"}

# NiceGUI UI
@ui.page('/')
def home_page(user_id: str = None):
    ui.query('.nicegui-content').classes('items-center')
    
    with ui.card().classes('w-96 p-6'):
        ui.label('Welcome to GYMO').classes('text-2xl font-bold text-center mb-4')
        
        if user_id:
            # We have a user ID from the query param, show user info
            import requests
            response = requests.get(f"http://{API_HOST}:{API_PORT}/check-session?user_id={user_id}")
            if response.status_code == 200 and "error" not in response.json():
                user = response.json()
                ui.label(f'Hello, {user.get("name", "User")}!').classes('text-lg text-center mb-2')
                ui.label(f'Email: {user.get("email", "No email")}').classes('text-sm text-center mb-4')
                ui.button('Protected Page', on_click=lambda: ui.navigate(f'/protected?user_id={user_id}')).classes('w-full bg-green-500 text-white mb-2')
                ui.button('Logout', on_click=lambda: ui.navigate(f'http://{API_HOST}:{API_PORT}/logout')).classes('w-full bg-red-500 text-white')
            else:
                # Invalid user ID
                ui.label('Please log in to continue').classes('text-center mb-4')
                ui.button('Login with Auth0', on_click=lambda: ui.navigate(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white')
        else:
            # No user ID provided
            ui.label('Please log in to continue').classes('text-center mb-4')
            ui.button('Login with Auth0', on_click=lambda: ui.navigate(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white')

@ui.page('/login-failed')
def login_failed():
    ui.query('.nicegui-content').classes('items-center')
    
    with ui.card().classes('w-96 p-6'):
        ui.label('Login Failed').classes('text-2xl font-bold text-center mb-4 text-red-500')
        ui.label('There was a problem authenticating your account.').classes('text-center mb-4')
        ui.button('Try Again', on_click=lambda: ui.navigate(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white mb-2')
        ui.button('Go Home', on_click=lambda: ui.navigate('/')).classes('w-full bg-gray-500 text-white')

@ui.page('/protected')
def protected_page(user_id: str = None):
    ui.query('.nicegui-content').classes('items-center')
    
    if not user_id:
        ui.navigate('/')
        return
    
    # Verify user is logged in
    import requests
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

# Run both servers
def run_api():
    uvicorn.run(api, host=API_HOST, port=API_PORT)

def run_ui():
    ui.run(port=UI_PORT, title="GYMO - Auth0 Authentication", favicon="💪")

if __name__ == "__main__":
    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api)
    api_thread.daemon = True
    api_thread.start()
    
    # Start UI server in the main thread
    run_ui()