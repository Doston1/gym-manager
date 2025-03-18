from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import httpx
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()

# Enable session storage
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

http_client = httpx.AsyncClient()

def get_user(request: Request):
    return request.session.get("user")

@app.get("/login")
async def login():
    auth_url = (
        f"https://{AUTH0_DOMAIN}/authorize?"
        f"response_type=code&client_id={AUTH0_CLIENT_ID}&"
        f"redirect_uri={AUTH0_CALLBACK_URL}&scope=openid profile email"
    )
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(request: Request, code: str):
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    token_payload = {
        "grant_type": "authorization_code",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": AUTH0_CALLBACK_URL,
    }

    token_response = await http_client.post(token_url, json=token_payload)
    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return {"error": "Failed to authenticate"}

    user_url = f"https://{AUTH0_DOMAIN}/userinfo"
    user_response = await http_client.get(user_url, headers={"Authorization": f"Bearer {access_token}"})
    user_data = user_response.json()

    request.session["user"] = user_data
    return RedirectResponse(url="/")

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    logout_url = (
        f"https://{AUTH0_DOMAIN}/v2/logout?"
        f"client_id={AUTH0_CLIENT_ID}&returnTo=http://localhost:8000"
    )
    return RedirectResponse(logout_url)
