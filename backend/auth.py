from datetime import date
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from backend.database import get_db, User
from backend.utils.oauth import get_oauth
from backend.utils.session import set_user_session, remove_user_session, get_user_session

oauth = get_oauth()

def setup_auth_routes(api: FastAPI):
    @api.get("/login")
    async def login(request: Request):
        print("DEBUG:auth.py, login function")
        redirect_uri = "http://127.0.0.1:8000/callback"
        return await oauth.auth0.authorize_redirect(request, redirect_uri)

    @api.get("/callback")
    async def callback(request: Request, db: Session = Depends(get_db)):
        print("DEBUG:auth.py, callback function")
        token = await oauth.auth0.authorize_access_token(request)
        user_info = token.get("userinfo")
        print("DEBUG:auth.py, user_info:", user_info)
        if user_info:
            user_id = user_info.get("sub")

            set_user_session(user_id, user_info)
            request.session["user_id"] = user_id

            # Save user to database
            db_user = db.query(User).filter(User.email == user_info["email"]).first()
            print("DEBUG:auth.py, db_user:", db_user.user_id)
            if not db_user:
                db_user = User(
                    email=user_info["email"],
                    first_name="temp_first_name",
                    last_name="temp_last_name",
                    phone="temp_phone",
                    date_of_birth= date(2021, 1, 1),
                    gender="male",
                    profile_image_path="temp_profile_image_path",
                    user_type="member",
                    firebase_uid=user_info["sid"]
                    )
                db.add(db_user)
                db.commit()
                db.refresh(db_user)

            return RedirectResponse(url=f'http://127.0.0.1:8080/?user_id={user_id}')
        return RedirectResponse(url="http://127.0.0.1:8080/login-failed")

    @api.get("/logout")
    async def logout(request: Request):
        user_id = request.session.pop("user_id", None)
        remove_user_session(user_id)
        return RedirectResponse(url=f"https://{oauth.auth0.client_kwargs['server_metadata_url']}/v2/logout?returnTo=http://127.0.0.1:8080/")
