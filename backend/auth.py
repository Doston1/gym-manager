from datetime import date, datetime
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
import requests
from backend.database.base import get_db_connection
from backend.database.crud import user as crud_user
from backend.utils.oauth import get_oauth
from frontend.config import API_HOST, UI_PORT, AUTH0_CLIENT_ID, AUTH0_DOMAIN, AUTH0_AUDIENCE
from jose import jwt, JWTError, ExpiredSignatureError
from mysql.connector import Error as DBError
import os


oauth = get_oauth()

def verify_jwt(token: str):
    try:
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

async def get_current_user_data(request: Request, db_conn = Depends(get_db_connection)):
    auth_header = request.headers.get('Authorization', '')
    token_str = auth_header.split(" ")[1] if " " in auth_header else None # Renamed to avoid conflict
    if not token_str:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        jwt_payload = verify_jwt(token_str)
        auth_id = jwt_payload.get("sub") # Changed firebase_uid to auth_id
        if not auth_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub (auth_id)")

        cursor = None
        try:
            cursor = db_conn.cursor(dictionary=True)
            user = crud_user.get_user_by_auth_id(db_conn, cursor, auth_id) # Changed
            if not user:
                raise HTTPException(status_code=404, detail="User not found in database")
            
            user_data_for_session = {
                "auth_id": user["auth_id"], # Changed
                "user_id": user["user_id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "user_type": user["user_type"],
            }
            if user["user_type"] == "member":
                member_details = crud_user.get_member_by_user_id_pk(db_conn, cursor, user["user_id"])
                if member_details: user_data_for_session["member_id_pk"] = member_details["member_id"]
            elif user["user_type"] == "trainer":
                trainer_details = crud_user.get_trainer_by_user_id_pk(db_conn, cursor, user["user_id"])
                if trainer_details: user_data_for_session["trainer_id_pk"] = trainer_details["trainer_id"] # PK of trainer table itself
            # Add manager details similarly

            return user_data_for_session

        finally:
            if cursor:
                cursor.close()

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except DBError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


def setup_auth_routes(api: FastAPI):
    @api.get("/login")
    async def login(request: Request):
        api_port = os.getenv("API_PORT", 8000) # Get API_PORT for redirect_url
        redirect_url = f"http://{API_HOST}:{api_port}/callback" 
        try:
            return await oauth.auth0.authorize_redirect(
                request,
                redirect_url,
                prompt="login"
            )
        except Exception as e:
            print("ERROR during authorize_redirect:", e)
            raise HTTPException(status_code=500, detail="Login failed")

    @api.get("/callback")
    async def callback(request: Request, db_conn = Depends(get_db_connection)):
        print("DEBUG:auth.py, callback function")
        token_data = await oauth.auth0.authorize_access_token(request) # Renamed token
        user_info = token_data.get("userinfo")
        
        if user_info:
            email = user_info.get("email")
            auth_id = user_info.get("sub") # Changed firebase_uid to auth_id

            if not email or not auth_id:
                raise HTTPException(status_code=400, detail="Email or Auth ID missing from token")

            cursor = None
            try:
                cursor = db_conn.cursor(dictionary=True) # Create cursor here for get_user_by_auth_id
                db_user = crud_user.get_user_by_auth_id(db_conn, cursor, auth_id) # Changed
                
                if not db_user:
                    full_name = user_info.get("name", "Temporary Name")
                    name_parts = full_name.split(" ", 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else "User"

                    new_user_data = {
                        "auth_id": auth_id, # Changed
                        "email": email,
                        "first_name": user_info.get("given_name", first_name),
                        "last_name": user_info.get("family_name", last_name),
                        "phone": user_info.get("phone_number"), # Allow None
                        "date_of_birth": None, # Allow None, user can fill later
                        "gender": user_info.get("gender"), # Allow None
                        "profile_image_path": user_info.get("picture"),
                        "user_type": "member",
                        "is_active": True
                    }
                    
                    member_details = { # Default member details for a new user
                        "weight": None, "height": None, "fitness_goal": "General Fitness",
                        "fitness_level": "Beginner", "health_conditions": None
                    }
                    new_user_data_with_member = {**new_user_data, "member_details": member_details}

                    created_user = crud_user.create_user_and_type(db_conn, new_user_data_with_member) 
                    print(f"DEBUG:auth.py, created_user.user_id (PK): {created_user['user_id']}")
                else:
                    print(f"DEBUG:auth.py, existing db_user.user_id (PK): {db_user['user_id']}")
                
                id_token = token_data.get('id_token')
                ui_host = os.getenv("UI_HOST", "127.0.0.1") # For frontend redirect
                ui_port = os.getenv("UI_PORT", "8080")
                frontend_redirect_url = f"http://{ui_host}:{ui_port}/" 
                if id_token:
                     frontend_redirect_url = f"http://{ui_host}:{ui_port}/static/callback.html#id_token={id_token}"
                
                return RedirectResponse(url=frontend_redirect_url)

            except DBError as e:
                raise HTTPException(status_code=500, detail=f"Database error: {e}")
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
            finally:
                if cursor:
                    cursor.close() # Close the cursor opened in this block

        ui_host = os.getenv("UI_HOST", "127.0.0.1")
        ui_port = os.getenv("UI_PORT", "8080")
        return RedirectResponse(url=f"http://{ui_host}:{ui_port}/login-failed")

    @api.get("/logout")
    async def logout(request: Request):
        ui_host = os.getenv("UI_HOST", "127.0.0.1")
        ui_port = os.getenv("UI_PORT", "8080")
        logout_url = f"https://{AUTH0_DOMAIN}/v2/logout?client_id={AUTH0_CLIENT_ID}&returnTo=http://{ui_host}:{ui_port}&federated"
        return RedirectResponse(url=logout_url)

    @api.get("/me")
    async def me(current_user_session_data: dict = Depends(get_current_user_data)):
        print(f"DEBUG: /me route - user_session_data =", current_user_session_data)
        return current_user_session_data