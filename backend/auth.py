from datetime import date
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
import requests
from sqlalchemy.orm import Session
from backend.database import get_db, User, Member
from backend.utils.oauth import get_oauth
from frontend.config import API_HOST, UI_PORT, AUTH0_CLIENT_ID, AUTH0_DOMAIN, AUTH0_AUDIENCE  # Import environment variables
from jose import jwt, JWTError, ExpiredSignatureError



oauth = get_oauth()

def verify_jwt(token: str):
    try:
        print("DEBUG: auth.pt - verify_jwt AUTH0_AUDIENCE:", AUTH0_AUDIENCE)
        jwks_url = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
        jwks = requests.get(jwks_url).json()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = next((key for key in jwks["keys"] if key["kid"] == unverified_header["kid"]), None)
        if rsa_key:
            payload = jwt.decode(
                token, rsa_key, algorithms=['RS256'],
                audience=AUTH0_AUDIENCE, issuer=f'https://{AUTH0_DOMAIN}/'
            )
            return payload
    except ExpiredSignatureError:
        print("❌ Token expired")
        raise
    except JWTError as e:
        print(f"❌ Token verification failed: {e}")
        raise

async def get_current_user(request: Request):
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.split(" ")[1] if " " in auth_header else None
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        user = verify_jwt(token)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def setup_auth_routes(api: FastAPI):
    @api.get("/login")
    async def login(request: Request):
        print("DEBUG:auth.py, login function")
        redirect_url = "http://127.0.0.1:8000/callback"
        try:
            return await oauth.auth0.authorize_redirect(
                request,
                redirect_url,
                prompt="login"
                )
        except Exception as e:
            print("ERROR during authorize_redirect:", e)
            raise HTTPException(status_code=500, detail="Login failed")
        # return await oauth.auth0.authorize_redirect(request, redirect_uri)

    @api.get("/callback")
    async def callback(request: Request, db: Session = Depends(get_db)):
        print("DEBUG:auth.py, callback function")
        token = await oauth.auth0.authorize_access_token(request)
        user_info = token.get("userinfo")
        print("DEBUG:auth.py, user_info:", user_info)

        if user_info:
            email = user_info.get("email")

            # Check if user exists
            db_user = db.query(User).filter(User.email == email).first()
            if not db_user:
                # Create new user
                db_user = User(
                    email=user_info["email"],
                    first_name="temp_first_name",
                    last_name="temp_last_name",
                    phone="temp_phone",
                    date_of_birth=date(2021, 1, 1),
                    gender="Male",
                    profile_image_path="temp_profile_image_path",
                    user_type="member",
                    firebase_uid=user_info["sub"]
                )
                db.add(db_user)
                db.commit()
                db.refresh(db_user)

                # Create corresponding member record
                new_member = Member(
                    user_id=db_user.user_id,
                    weight=70.0,  # default temporary weight
                    height=170.0,  # default temporary height
                    fitness_goal="General Fitness",  # default goal
                    fitness_level="Beginner",  # default level
                    health_conditions="None specified"  # default health conditions
                )
                db.add(new_member)
                db.commit()

            print("DEBUG:auth.py, db_user:", db_user.user_id)    
            id_token = token.get('id_token')
            frontend_redirect = f"http://127.0.0.1:8080/static/callback.html#id_token={id_token}"
            return RedirectResponse(url=frontend_redirect)
        return RedirectResponse(url="http://127.0.0.1:8080/login-failed")


    @api.get("/logout")
    async def logout(request: Request):
        logout_url = f"https://{AUTH0_DOMAIN}/v2/logout?client_id={AUTH0_CLIENT_ID}&returnTo=http://{API_HOST}:{UI_PORT}&federated"
        return RedirectResponse(url=logout_url)


    @api.get("/me")
    async def me(user: dict = Depends(get_current_user)):
        print("DEBUG: /me route - user =", user)
        return {"user_id": user["sub"], "email": user["email"], "name": user["name"]}

