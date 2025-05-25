from datetime import date
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
import requests
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models.user import User, Member, Trainer, Manager, UserTypeEnum, GenderEnum # Make sure UserTypeEnum is imported
from backend.database.crud.user import get_user_by_firebase_uid, get_member_by_user_id, get_trainer_by_user_id, get_manager_by_user_id # Import CRUD functions
from backend.utils.oauth import get_oauth
from frontend.config import API_HOST, API_PORT, UI_PORT, AUTH0_CLIENT_ID, AUTH0_DOMAIN, AUTH0_AUDIENCE
from jose import jwt, JWTError, ExpiredSignatureError


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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError as e:
        print(f"❌ Token verification failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        print(f"❌ An unexpected error occurred during token verification: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token verification error")


async def get_current_user_auth_info(request: Request): # Renamed to avoid clash if used elsewhere
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.split(" ")[1] if " " in auth_header else None
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated: No token provided")
    try:
        user_auth_payload = verify_jwt(token)
        return user_auth_payload
    except HTTPException as e: # Re-raise HTTPExceptions from verify_jwt
        raise e
    except Exception as e: # Catch other unexpected errors
        print(f"❌ Error in get_current_user_auth_info: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication error")


def setup_auth_routes(api: FastAPI):
    @api.get("/login")
    async def login(request: Request):
        redirect_url = f"http://{API_HOST}:{API_PORT}/callback" # Ensure API_PORT is used here
        try:
            return await oauth.auth0.authorize_redirect(
                request,
                redirect_url,
                prompt="login" # Forces login prompt
            )
        except Exception as e:
            print(f"ERROR during authorize_redirect: {e}")
            raise HTTPException(status_code=500, detail="Login failed")

    @api.get("/callback")
    async def callback(request: Request, db: Session = Depends(get_db)):
        try:
            token = await oauth.auth0.authorize_access_token(request)
            user_info = token.get("userinfo")
            print("DEBUG:auth.py, user_info:", user_info)

            if user_info:
                email = user_info.get("email")
                firebase_uid = user_info.get("sub") # Auth0 'sub' is the user ID

                db_user = get_user_by_firebase_uid(db, firebase_uid)
                if not db_user:
                    # Create new user
                    db_user = User(
                        firebase_uid=firebase_uid,
                        email=email,
                        first_name=user_info.get("given_name", "temp_first_name"),
                        last_name=user_info.get("family_name", "temp_last_name"),
                        phone="temp_phone", # Placeholder
                        date_of_birth=date(2000, 1, 1), # Placeholder
                        gender=GenderEnum.PreferNotToSay, # Placeholder from your user model
                        profile_image_path="temp_profile_image_path", # Placeholder
                        user_type=UserTypeEnum.member # Default to member
                    )
                    db.add(db_user)
                    db.commit()
                    db.refresh(db_user)

                    # Create corresponding member record if user_type is member
                    if db_user.user_type == UserTypeEnum.member:
                        new_member = Member(
                            user_id=db_user.user_id,
                            # Add other default member fields if necessary
                        )
                        db.add(new_member)
                        db.commit()

                id_token = token.get('id_token')
                # Redirect to frontend callback handler which stores the token
                frontend_redirect = f"http://{API_HOST}:{UI_PORT}/static/callback.html#id_token={id_token}"
                return RedirectResponse(url=frontend_redirect)
            
            print("Error: User info not found in token.")
            return RedirectResponse(url=f"http://{API_HOST}:{UI_PORT}/login-failed?error=no_user_info")
        except Exception as e:
            print(f"Error in callback: {e}")
            return RedirectResponse(url=f"http://{API_HOST}:{UI_PORT}/login-failed?error=callback_exception")


    @api.get("/logout")
    async def logout(request: Request):
        # Clear any server-side session if you implement one (not the case here with token-based)
        # Construct Auth0 logout URL
        auth0_logout_url = (
            f"https://{AUTH0_DOMAIN}/v2/logout"
            f"?client_id={AUTH0_CLIENT_ID}"
            f"&returnTo=http://{API_HOST}:{UI_PORT}" # Redirect back to UI home after logout
        )
        return RedirectResponse(url=auth0_logout_url)

    @api.get("/me", response_model=dict) # Using dict for flexibility, define a Pydantic model for better practice
    async def me(user_auth_info: dict = Depends(get_current_user_auth_info), db: Session = Depends(get_db)):
        firebase_uid = user_auth_info.get("sub")
        if not firebase_uid:
            raise HTTPException(status_code=400, detail="Firebase UID not found in token")

        db_user = get_user_by_firebase_uid(db, firebase_uid)
        if not db_user:
            # This case should ideally be handled during callback, but as a fallback:
            # Potentially create the user here if they exist in Auth0 but not in local DB
            # For now, assume user must exist post-callback.
            raise HTTPException(status_code=404, detail="User not found in application database")

        user_details = {
            "user_db_id": db_user.user_id, # Your internal auto-incrementing user_id
            "firebase_uid": db_user.firebase_uid,
            "email": db_user.email,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "name": f"{db_user.first_name} {db_user.last_name}", # For convenience
            "user_type": db_user.user_type.value if db_user.user_type else None,
            "member_id": None,
            "trainer_id": None,
            "manager_id": None,
        }

        if db_user.user_type == UserTypeEnum.member:
            member_record = get_member_by_user_id(db, db_user.user_id)
            if member_record:
                user_details["member_id"] = member_record.member_id
        elif db_user.user_type == UserTypeEnum.trainer:
            trainer_record = get_trainer_by_user_id(db, db_user.user_id)
            if trainer_record:
                user_details["trainer_id"] = trainer_record.trainer_id
        elif db_user.user_type == UserTypeEnum.manager:
            manager_record = get_manager_by_user_id(db, db_user.user_id)
            if manager_record:
                user_details["manager_id"] = manager_record.manager_id
                
        print(f"DEBUG: /me route - user_details = {user_details}")
        return user_details


# ================== OLD VERSION ==================
# from datetime import date
# from fastapi import FastAPI, Depends, HTTPException, status, Request
# from fastapi.responses import RedirectResponse
# import requests
# from sqlalchemy.orm import Session
# from backend.database import get_db, User, Member
# from backend.utils.oauth import get_oauth
# from frontend.config import API_HOST, UI_PORT, AUTH0_CLIENT_ID, AUTH0_DOMAIN, AUTH0_AUDIENCE  # Import environment variables
# from jose import jwt, JWTError, ExpiredSignatureError



# oauth = get_oauth()

# def verify_jwt(token: str):
#     try:
#         print("DEBUG: auth.pt - verify_jwt AUTH0_AUDIENCE:", AUTH0_AUDIENCE)
#         jwks_url = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
#         jwks = requests.get(jwks_url).json()
#         unverified_header = jwt.get_unverified_header(token)
#         rsa_key = next((key for key in jwks["keys"] if key["kid"] == unverified_header["kid"]), None)
#         if rsa_key:
#             payload = jwt.decode(
#                 token, rsa_key, algorithms=['RS256'],
#                 audience=AUTH0_AUDIENCE, issuer=f'https://{AUTH0_DOMAIN}/'
#             )
#             return payload
#     except ExpiredSignatureError:
#         print("❌ Token expired")
#         raise
#     except JWTError as e:
#         print(f"❌ Token verification failed: {e}")
#         raise

# async def get_current_user(request: Request):
#     auth_header = request.headers.get('Authorization', '')
#     token = auth_header.split(" ")[1] if " " in auth_header else None
#     if not token:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#     try:
#         user = verify_jwt(token)
#         return user
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


# def setup_auth_routes(api: FastAPI):
#     @api.get("/login")
#     async def login(request: Request):
#         print("DEBUG:auth.py, login function")
#         redirect_url = "http://127.0.0.1:8000/callback"
#         try:
#             return await oauth.auth0.authorize_redirect(
#                 request,
#                 redirect_url,
#                 prompt="login"
#                 )
#         except Exception as e:
#             print("ERROR during authorize_redirect:", e)
#             raise HTTPException(status_code=500, detail="Login failed")
#         # return await oauth.auth0.authorize_redirect(request, redirect_uri)

#     @api.get("/callback")
#     async def callback(request: Request, db: Session = Depends(get_db)):
#         print("DEBUG:auth.py, callback function")
#         token = await oauth.auth0.authorize_access_token(request)
#         user_info = token.get("userinfo")
#         print("DEBUG:auth.py, user_info:", user_info)

#         if user_info:
#             email = user_info.get("email")

#             # Check if user exists
#             db_user = db.query(User).filter(User.email == email).first()
#             if not db_user:
#                 # Create new user
#                 db_user = User(
#                     email=user_info["email"],
#                     first_name="temp_first_name",
#                     last_name="temp_last_name",
#                     phone="temp_phone",
#                     date_of_birth=date(2021, 1, 1),
#                     gender="Male",
#                     profile_image_path="temp_profile_image_path",
#                     user_type="member",
#                     firebase_uid=user_info["sub"]
#                 )
#                 db.add(db_user)
#                 db.commit()
#                 db.refresh(db_user)

#                 # Create corresponding member record
#                 new_member = Member(
#                     user_id=db_user.user_id,
#                     weight=70.0,  # default temporary weight
#                     height=170.0,  # default temporary height
#                     fitness_goal="General Fitness",  # default goal
#                     fitness_level="Beginner",  # default level
#                     health_conditions="None specified"  # default health conditions
#                 )
#                 db.add(new_member)
#                 db.commit()

#             print("DEBUG:auth.py, db_user:", db_user.user_id)    
#             id_token = token.get('id_token')
#             frontend_redirect = f"http://127.0.0.1:8080/static/callback.html#id_token={id_token}"
#             return RedirectResponse(url=frontend_redirect)
#         return RedirectResponse(url="http://127.0.0.1:8080/login-failed")


#     @api.get("/logout")
#     async def logout(request: Request):
#         logout_url = f"https://{AUTH0_DOMAIN}/v2/logout?client_id={AUTH0_CLIENT_ID}&returnTo=http://{API_HOST}:{UI_PORT}&federated"
#         return RedirectResponse(url=logout_url)


#     @api.get("/me")
#     async def me(user: dict = Depends(get_current_user)):
#         print("DEBUG: /me route - user =", user)
#         return {"user_id": user["sub"], "email": user["email"], "name": user["name"]}

