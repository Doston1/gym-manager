Okay, this is a comprehensive project! I will provide the necessary code modifications and new implementations to achieve the training scheduling and live dashboard features. This will involve touching many files.

Given the scope, I'll focus on the core logic and connections for these features. Some UI niceties or very minor helper functions might be omitted for brevity but the structural components and data flow will be addressed.

**Important Assumptions:**

1.  The database models in `backend/database/models/training.py` (and other model files) correctly reflect the schemas in `backend/database/saved_queries/new_tables_queries.py`.
2.  The corresponding Pydantic schemas in `backend/database/schemas/training.py` are also up-to-date with these models.
3.  The Auth0 setup is functional, and the frontend correctly stores the `id_token` in `localStorage` as 'token'.
4.  Basic CRUD operations for supporting entities (like `Hall`, `Trainer`, `Exercise`, `TrainingPlan`) are functional or will be added as needed.

**Plan of Action:**

1.  **Enhance Backend Authentication**: Modify `/me` endpoint to return user type and role-specific IDs.
2.  **Backend for Preferences**: Implement API endpoints and CRUD for `TrainingPreference`.
3.  **Backend Scheduling Logic**: Create a new `scheduler.py` module and integrate it with FastAPI using APScheduler.
4.  **Backend for Weekly Schedule & Live Sessions**: Implement API endpoints and CRUD for `WeeklySchedule`, `ScheduleMember`, `LiveSession`, `LiveSessionExercise`.
5.  **Frontend - Training Preferences**: Update UI and logic.
6.  **Frontend - Weekly Schedule**: Update UI and logic for different roles.
7.  **Frontend - Live Dashboard**: Update UI and logic for different roles.
8.  **Frontend - My Training Plans (History)**: Update UI to show training history.
9.  **Integrate Scheduling Algorithms**: Adapt concepts from Meetly for rescheduling/optimization (conceptual outline for now, as full adaptation is complex).

Let's start with the modifications.

**Phase 1: Backend Enhancements**

**File: `backend/auth.py`** (Enhance `/me` endpoint)

```python
from datetime import date
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
import requests
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models.user import User, Member, Trainer, Manager, UserTypeEnum # Make sure UserTypeEnum is imported
from backend.database.crud.user import get_user_by_firebase_uid, get_member_by_user_id, get_trainer_by_user_id, get_manager_by_user_id # Import CRUD functions
from backend.utils.oauth import get_oauth
from frontend.config import API_HOST, UI_PORT, AUTH0_CLIENT_ID, AUTH0_DOMAIN, AUTH0_AUDIENCE
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

```

**File: `backend/database/crud/training.py`** (Add/Update CRUD functions)
This file already contains a good base. I'll ensure it aligns with the new models and add any missing crucial functions, especially for querying data needed by the scheduler and live dashboard.

```python
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time, timedelta

from ..models.training import (
    TrainingPreference,
    WeeklySchedule,
    ScheduleMember,
    LiveSession,
    LiveSessionExercise,
    LiveSessionAttendance,
    TrainingCycle,
    Exercise  # Make sure Exercise is imported
)
from ..models.user import User, Member, Trainer # For joins
from ..models.facility import Hall # For joins
from ..schemas.training import (
    TrainingPreferenceCreate,
    TrainingPreferenceUpdate,
    WeeklyScheduleCreate,
    WeeklyScheduleUpdate,
    ScheduleMemberCreate,
    ScheduleMemberUpdate,
    LiveSessionCreate,
    LiveSessionUpdate,
    LiveSessionExerciseCreate,
    LiveSessionExerciseUpdate,
    LiveSessionAttendanceCreate,
    LiveSessionAttendanceUpdate,
    TrainingCycleCreate,
    TrainingCycleUpdate,
    ScheduleStatus,
    ScheduleMemberStatus,
    LiveSessionStatus,
    AttendanceStatus,
    CycleStatus,
    DayOfWeek as DayOfWeekEnum # Import DayOfWeek enum from schemas if defined there
)
from ..database.base import SessionLocal # For scheduler

# --- Training Preferences ---
def get_training_preference(db: Session, preference_id: int) -> Optional[TrainingPreference]:
    return db.query(TrainingPreference).filter(TrainingPreference.preference_id == preference_id).first()

def get_member_preferences_for_week(db: Session, member_id: int, week_start_date: date) -> List[TrainingPreference]:
    return db.query(TrainingPreference).filter(
        TrainingPreference.member_id == member_id,
        TrainingPreference.week_start_date == week_start_date
    ).all()

def create_training_preference(db: Session, preference_in: TrainingPreferenceCreate) -> TrainingPreference:
    # Check for existing preference for the same slot
    existing_preference = db.query(TrainingPreference).filter(
        TrainingPreference.member_id == preference_in.member_id,
        TrainingPreference.week_start_date == preference_in.week_start_date,
        TrainingPreference.day_of_week == preference_in.day_of_week,
        TrainingPreference.start_time == preference_in.start_time,
        TrainingPreference.end_time == preference_in.end_time
    ).first()

    if existing_preference:
        # Update existing preference
        existing_preference.preference_type = preference_in.preference_type
        existing_preference.trainer_id = preference_in.trainer_id
        db_preference = existing_preference
    else:
        # Create new preference
        db_preference = TrainingPreference(**preference_in.dict())
        db.add(db_preference)

    db.commit()
    db.refresh(db_preference)
    return db_preference

def update_training_preference(db: Session, preference_id: int, preference_in: TrainingPreferenceUpdate) -> Optional[TrainingPreference]:
    db_preference = get_training_preference(db, preference_id)
    if db_preference:
        update_data = preference_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_preference, key, value)
        db.commit()
        db.refresh(db_preference)
    return db_preference

def delete_training_preference(db: Session, preference_id: int) -> bool:
    db_preference = get_training_preference(db, preference_id)
    if db_preference:
        db.delete(db_preference)
        db.commit()
        return True
    return False

def get_all_preferences_for_week(db: Session, week_start_date: date) -> List[TrainingPreference]:
    return db.query(TrainingPreference).filter(TrainingPreference.week_start_date == week_start_date).all()


# --- Weekly Schedule ---
def get_weekly_schedule_by_id(db: Session, schedule_id: int) -> Optional[WeeklySchedule]:
    return db.query(WeeklySchedule).filter(WeeklySchedule.schedule_id == schedule_id).first()

def get_schedules_for_week(db: Session, week_start_date: date, trainer_id: Optional[int] = None, hall_id: Optional[int] = None) -> List[WeeklySchedule]:
    query = db.query(WeeklySchedule).filter(WeeklySchedule.week_start_date == week_start_date)
    if trainer_id:
        query = query.filter(WeeklySchedule.trainer_id == trainer_id)
    if hall_id:
        query = query.filter(WeeklySchedule.hall_id == hall_id)
    return query.order_by(WeeklySchedule.day_of_week, WeeklySchedule.start_time).all()

def create_weekly_schedule_entry(db: Session, schedule_in: WeeklyScheduleCreate) -> WeeklySchedule:
    db_schedule = WeeklySchedule(**schedule_in.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def update_weekly_schedule_entry(db: Session, schedule_id: int, schedule_in: WeeklyScheduleUpdate) -> Optional[WeeklySchedule]:
    db_schedule = get_weekly_schedule_by_id(db, schedule_id)
    if db_schedule:
        update_data = schedule_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_schedule, key, value)
        db_schedule.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_schedule)
    return db_schedule

def delete_weekly_schedule_entries_for_week(db: Session, week_start_date: date):
    db.query(WeeklySchedule).filter(WeeklySchedule.week_start_date == week_start_date).delete()
    db.commit()

def add_member_to_schedule_entry(db: Session, schedule_member_in: ScheduleMemberCreate) -> ScheduleMember:
    db_schedule_member = ScheduleMember(**schedule_member_in.dict())
    db.add(db_schedule_member)
    db.commit()
    db.refresh(db_schedule_member)
    return db_schedule_member

def get_member_schedules_for_week(db: Session, member_id: int, week_start_date: date) -> List[WeeklySchedule]:
    return db.query(WeeklySchedule)\
        .join(ScheduleMember, WeeklySchedule.schedule_id == ScheduleMember.schedule_id)\
        .filter(ScheduleMember.member_id == member_id, WeeklySchedule.week_start_date == week_start_date)\
        .order_by(WeeklySchedule.day_of_week, WeeklySchedule.start_time)\
        .all()

def get_trainer_schedules_for_week(db: Session, trainer_id: int, week_start_date: date) -> List[WeeklySchedule]:
    return db.query(WeeklySchedule)\
        .filter(WeeklySchedule.trainer_id == trainer_id, WeeklySchedule.week_start_date == week_start_date)\
        .order_by(WeeklySchedule.day_of_week, WeeklySchedule.start_time)\
        .all()

def get_schedule_members(db: Session, schedule_id: int) -> List[ScheduleMember]:
    return db.query(ScheduleMember).filter(ScheduleMember.schedule_id == schedule_id).all()

def update_schedule_member_status(db: Session, schedule_member_id: int, status: ScheduleMemberStatus) -> Optional[ScheduleMember]:
    sm = db.query(ScheduleMember).filter(ScheduleMember.id == schedule_member_id).first()
    if sm:
        sm.status = status
        db.commit()
        db.refresh(sm)
    return sm

# --- Live Sessions ---
def create_live_session(db: Session, schedule_id: int, notes: Optional[str] = None) -> LiveSession:
    # Check if a live session already exists for this schedule_id and is not completed/cancelled
    existing_session = db.query(LiveSession).filter(
        LiveSession.schedule_id == schedule_id,
        LiveSession.status.notin_([LiveSessionStatus.completed, LiveSessionStatus.cancelled])
    ).first()
    if existing_session:
        return existing_session # Return existing active session

    db_live_session = LiveSession(
        schedule_id=schedule_id,
        status=LiveSessionStatus.started,
        notes=notes
    )
    db.add(db_live_session)
    db.commit()
    db.refresh(db_live_session)
    return db_live_session

def get_live_session_by_id(db: Session, live_session_id: int) -> Optional[LiveSession]:
    return db.query(LiveSession).filter(LiveSession.live_session_id == live_session_id).first()

def get_live_session_by_schedule_id(db: Session, schedule_id: int) -> Optional[LiveSession]:
    return db.query(LiveSession).filter(LiveSession.schedule_id == schedule_id).order_by(LiveSession.created_at.desc()).first()


def update_live_session_status(db: Session, live_session_id: int, status: LiveSessionStatus, end_time: Optional[datetime] = None) -> Optional[LiveSession]:
    ls = get_live_session_by_id(db, live_session_id)
    if ls:
        ls.status = status
        if end_time:
            ls.end_time = end_time
        ls.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ls)
    return ls

def get_active_live_session_for_member(db: Session, member_id: int) -> Optional[LiveSession]:
    now = datetime.utcnow()
    return db.query(LiveSession)\
        .join(WeeklySchedule, LiveSession.schedule_id == WeeklySchedule.schedule_id)\
        .join(ScheduleMember, WeeklySchedule.schedule_id == ScheduleMember.schedule_id)\
        .filter(ScheduleMember.member_id == member_id)\
        .filter(LiveSession.status.in_([LiveSessionStatus.started, LiveSessionStatus.in_progress]))\
        .filter(WeeklySchedule.day_of_week == DayOfWeekEnum(now.strftime('%A')))\
        .filter(WeeklySchedule.start_time <= now.time())\
        .filter(WeeklySchedule.end_time >= now.time())\
        .first()

def get_active_live_session_for_trainer(db: Session, trainer_id: int) -> Optional[LiveSession]:
    now = datetime.utcnow()
    return db.query(LiveSession)\
        .join(WeeklySchedule, LiveSession.schedule_id == WeeklySchedule.schedule_id)\
        .filter(WeeklySchedule.trainer_id == trainer_id)\
        .filter(LiveSession.status.in_([LiveSessionStatus.started, LiveSessionStatus.in_progress]))\
        .filter(WeeklySchedule.day_of_week == DayOfWeekEnum(now.strftime('%A')))\
        .filter(WeeklySchedule.start_time <= now.time())\
        .filter(WeeklySchedule.end_time >= now.time())\
        .first()

def get_all_active_live_sessions(db: Session) -> List[LiveSession]:
    now = datetime.utcnow()
    return db.query(LiveSession)\
        .join(WeeklySchedule, LiveSession.schedule_id == WeeklySchedule.schedule_id)\
        .filter(LiveSession.status.in_([LiveSessionStatus.started, LiveSessionStatus.in_progress]))\
        .filter(WeeklySchedule.day_of_week == DayOfWeekEnum(now.strftime('%A')))\
        .filter(WeeklySchedule.start_time <= now.time())\
        .filter(WeeklySchedule.end_time >= now.time())\
        .all()

# --- Live Session Exercises ---
def add_or_update_live_session_exercise(db: Session, exercise_in: LiveSessionExerciseCreate) -> LiveSessionExercise:
    db_exercise = db.query(LiveSessionExercise).filter(
        LiveSessionExercise.live_session_id == exercise_in.live_session_id,
        LiveSessionExercise.member_id == exercise_in.member_id,
        LiveSessionExercise.exercise_id == exercise_in.exercise_id
    ).first()

    if db_exercise: # Update existing
        db_exercise.sets_completed = exercise_in.sets_completed
        db_exercise.actual_reps = exercise_in.actual_reps
        db_exercise.weight_used = exercise_in.weight_used
        db_exercise.comments = exercise_in.comments
        db_exercise.updated_at = datetime.utcnow()
    else: # Create new
        db_exercise = LiveSessionExercise(**exercise_in.dict(), completed=False)
        db.add(db_exercise)

    db.commit()
    db.refresh(db_exercise)
    return db_exercise

def complete_live_session_exercise(db: Session, live_session_id: int, member_id: int, exercise_id: int) -> Optional[LiveSessionExercise]:
    db_exercise = db.query(LiveSessionExercise).filter(
        LiveSessionExercise.live_session_id == live_session_id,
        LiveSessionExercise.member_id == member_id,
        LiveSessionExercise.exercise_id == exercise_id
    ).first()
    if db_exercise:
        db_exercise.completed = True
        db_exercise.completed_at = datetime.utcnow()
        db_exercise.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_exercise)
    return db_exercise

def get_live_session_exercises_for_member(db: Session, live_session_id: int, member_id: int) -> List[LiveSessionExercise]:
    return db.query(LiveSessionExercise)\
        .filter(LiveSessionExercise.live_session_id == live_session_id, LiveSessionExercise.member_id == member_id)\
        .join(Exercise).add_columns(Exercise.name.label("exercise_name"), Exercise.instructions, Exercise.image_url, Exercise.primary_muscle_group)\
        .all()

def get_live_session_exercises_for_trainer_view(db: Session, live_session_id: int) -> List[Dict[str, Any]]:
    # This query needs to get all members in the session and their exercises
    results = db.query(
        Member.member_id,
        User.first_name,
        User.last_name,
        Exercise.exercise_id,
        Exercise.name.label("exercise_name"),
        LiveSessionExercise.sets_completed,
        LiveSessionExercise.actual_reps,
        LiveSessionExercise.weight_used,
        LiveSessionExercise.completed
    ).select_from(LiveSession)\
    .join(ScheduleMember, ScheduleMember.schedule_id == LiveSession.schedule_id)\
    .join(Member, Member.member_id == ScheduleMember.member_id)\
    .join(User, User.user_id == Member.user_id)\
    .outerjoin(LiveSessionExercise, and_(
        LiveSessionExercise.live_session_id == LiveSession.live_session_id,
        LiveSessionExercise.member_id == Member.member_id
    ))\
    .outerjoin(Exercise, Exercise.exercise_id == LiveSessionExercise.exercise_id)\
    .filter(LiveSession.live_session_id == live_session_id)\
    .all()

    # Structure data for frontend:
    # { member_id: { first_name, last_name, exercises: [ {exercise_details...} ] } }
    # This part would need more complex processing or rely on relationship loading in SQLAlchemy if models are set up for it.
    # For now, returning flat list and frontend can group.
    return [row._asdict() for row in results]


def get_member_training_history(db: Session, member_id: int, plan_id: Optional[int] = None) -> List[LiveSessionExercise]:
    query = db.query(LiveSessionExercise)\
        .filter(LiveSessionExercise.member_id == member_id)\
        .join(LiveSession).join(WeeklySchedule).join(Exercise)\
        .add_columns(
            LiveSession.start_time.label("session_start_time"),
            WeeklySchedule.day_of_week.label("session_day"),
            Exercise.name.label("exercise_name")
        )\
        .order_by(LiveSession.start_time.desc())

    # if plan_id: # This requires linking LiveSessionExercise back to a TrainingPlan, which is not direct.
    # This needs a more complex query or a different data model approach if history is per plan.
    # For now, it returns all history for the member.
    return query.all()


# --- Utility for Scheduler ---
def get_trainers_available_at_slot(db: Session, week_start_date: date, day_of_week: DayOfWeekEnum, start_time: time, end_time: time) -> List[Trainer]:
    # Subquery to find trainers already scheduled at this specific time slot
    scheduled_trainers = db.query(WeeklySchedule.trainer_id)\
        .filter(
            WeeklySchedule.week_start_date == week_start_date,
            WeeklySchedule.day_of_week == day_of_week,
            WeeklySchedule.start_time < end_time, # Check for overlap
            WeeklySchedule.end_time > start_time   # Check for overlap
        ).subquery()

    # Query for trainers NOT in the subquery
    available_trainers = db.query(Trainer)\
        .join(User, Trainer.user_id == User.user_id)\
        .filter(
            User.is_active == True,
            Trainer.trainer_id.notin_(scheduled_trainers)
        ).all()
    return available_trainers

def get_halls_available_at_slot(db: Session, week_start_date: date, day_of_week: DayOfWeekEnum, start_time: time, end_time: time) -> List[Hall]:
    # Subquery to find halls already scheduled at this specific time slot
    scheduled_halls = db.query(WeeklySchedule.hall_id)\
        .filter(
            WeeklySchedule.week_start_date == week_start_date,
            WeeklySchedule.day_of_week == day_of_week,
            WeeklySchedule.start_time < end_time,
            WeeklySchedule.end_time > start_time
        ).subquery()

    # Query for halls NOT in the subquery
    available_halls = db.query(Hall)\
        .filter(
            Hall.is_active == True,
            Hall.hall_id.notin_(scheduled_halls)
        ).all()
    return available_halls
```

**File: `backend/scheduling/scheduler.py`** (New File)
This will contain the core scheduling logic.

```python
from sqlalchemy.orm import Session
from datetime import date, time, timedelta
from collections import defaultdict
import random

from backend.database.crud import training as crud_training
from backend.database.models.training import TrainingPreference, WeeklySchedule, ScheduleMember, Hall, Trainer
from backend.database.schemas.training import WeeklyScheduleCreate, ScheduleMemberCreate, PreferenceType, DayOfWeek as DayOfWeekEnum, ScheduleStatus
from backend.database import SessionLocal, User # Assuming User is needed for created_by

# Configuration (could be moved to a config file or DB)
MIN_MEMBERS_FOR_SESSION = 1 # Minimum members to create a session
DEFAULT_SESSION_DURATION_MINUTES = 90 # Default duration if not specified by preference end_time

def get_next_week_start_date(today: Optional[date] = None) -> date:
    if today is None:
        today = date.today()
    # Next week starts on Sunday. day.weekday(): Mon=0, Sun=6
    days_until_sunday = (6 - today.weekday()) % 7
    if days_until_sunday == 0 and today.weekday() != 6 : # if today is not sunday but calculation is 0, means next sunday
         days_until_sunday = 7
    elif today.weekday() == 6: # if today is sunday, schedule for next sunday
        days_until_sunday = 7

    next_sunday = today + timedelta(days=days_until_sunday)
    return next_sunday


def run_initial_scheduling():
    """
    Runs on Friday 00:00.
    Schedules trainings for the next week based on member preferences, hall capacity, and trainer availability.
    """
    db: Session = SessionLocal()
    try:
        manager_user_id = 1 # Placeholder for system/manager user ID that creates the schedule
        # Fetch a default manager user or a system user ID
        manager_user = db.query(User).filter(User.user_type == 'manager').first() # Or some specific system user
        if manager_user:
            manager_user_id = manager_user.user_id
        else: # Fallback if no manager found, though this should be handled better
            print("Warning: No manager user found for 'created_by' field in schedule. Using placeholder.")


        target_week_start_date = get_next_week_start_date()
        print(f"Running initial scheduling for week starting: {target_week_start_date}")

        # 1. Clear any existing "Scheduled" entries for the target week to allow fresh scheduling
        # Be cautious with this in production. Maybe only clear if it's the first run for the week.
        db.query(WeeklySchedule).filter(
            WeeklySchedule.week_start_date == target_week_start_date,
            WeeklySchedule.status == ScheduleStatus.scheduled # Only clear non-started ones
        ).delete(synchronize_session=False)
        db.commit()

        # 2. Fetch all preferences for the target week
        preferences = crud_training.get_all_preferences_for_week(db, target_week_start_date)
        if not preferences:
            print("No training preferences found for the target week.")
            return

        # 3. Group preferences by (day, start_time, end_time)
        #    And also by trainer preference if specified
        slot_preferences = defaultdict(lambda: {'members': [], 'trainer_prefs': defaultdict(int)})
        for pref in preferences:
            if pref.preference_type in [PreferenceType.preferred, PreferenceType.available]:
                slot_key = (pref.day_of_week, pref.start_time, pref.end_time)
                slot_preferences[slot_key]['members'].append({
                    'member_id': pref.member_id,
                    'type': pref.preference_type,
                    'preferred_trainer_id': pref.trainer_id
                })
                if pref.trainer_id:
                    slot_preferences[slot_key]['trainer_prefs'][pref.trainer_id] += 1

        # 4. Iterate through popular slots and try to schedule
        # Sort slots by number of interested members (descending)
        sorted_slots = sorted(slot_preferences.items(), key=lambda item: len(item[1]['members']), reverse=True)

        for slot_key, data in sorted_slots:
            day_of_week, start_time, end_time = slot_key
            members_data = data['members']
            trainer_preference_counts = data['trainer_prefs']

            if len(members_data) < MIN_MEMBERS_FOR_SESSION:
                continue # Skip if not enough members

            # 5. Find available halls
            available_halls = crud_training.get_halls_available_at_slot(db, target_week_start_date, day_of_week, start_time, end_time)
            if not available_halls:
                print(f"No halls available for {day_of_week.value} {start_time}-{end_time}")
                continue

            # 6. Find available trainers
            available_trainers = crud_training.get_trainers_available_at_slot(db, target_week_start_date, day_of_week, start_time, end_time)
            if not available_trainers:
                print(f"No trainers available for {day_of_week.value} {start_time}-{end_time}")
                continue

            # Attempt to match preferred trainer first, then any available trainer
            chosen_trainer_id = None
            if trainer_preference_counts:
                # Sort preferred trainers by preference count
                sorted_preferred_trainers = sorted(trainer_preference_counts.items(), key=lambda item: item[1], reverse=True)
                for pt_id, _ in sorted_preferred_trainers:
                    if any(t.trainer_id == pt_id for t in available_trainers):
                        chosen_trainer_id = pt_id
                        break

            if not chosen_trainer_id and available_trainers:
                chosen_trainer_id = random.choice(available_trainers).trainer_id # Simple random choice

            if not chosen_trainer_id:
                print(f"Could not assign a trainer for {day_of_week.value} {start_time}-{end_time}")
                continue

            # Choose a hall (e.g., first available, or smallest that fits, or random)
            # For now, pick the first one that can hold MIN_MEMBERS_FOR_SESSION
            chosen_hall = None
            for hall in sorted(available_halls, key=lambda h: h.max_capacity): # Try smaller halls first
                if hall.max_capacity >= MIN_MEMBERS_FOR_SESSION:
                    chosen_hall = hall
                    break

            if not chosen_hall:
                print(f"No suitable hall found for {day_of_week.value} {start_time}-{end_time} with capacity for {len(members_data)} members.")
                continue

            # 7. Create WeeklySchedule entry
            schedule_create = WeeklyScheduleCreate(
                week_start_date=target_week_start_date,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                hall_id=chosen_hall.hall_id,
                trainer_id=chosen_trainer_id,
                max_capacity=chosen_hall.max_capacity,
                status=ScheduleStatus.scheduled,
                created_by=manager_user_id
            )
            new_schedule_entry = crud_training.create_weekly_schedule_entry(db, schedule_create)
            print(f"Scheduled: {new_schedule_entry.schedule_id} for {day_of_week.value} {start_time} at Hall {chosen_hall.name} with Trainer {chosen_trainer_id}")

            # 8. Assign members
            assigned_count = 0
            # Prioritize 'Preferred' members
            preferred_members = [m for m in members_data if m['type'] == PreferenceType.preferred]
            available_members = [m for m in members_data if m['type'] == PreferenceType.available]

            # Shuffle to give some randomness if many have same preference
            random.shuffle(preferred_members)
            random.shuffle(available_members)

            for member_data in preferred_members:
                if assigned_count < new_schedule_entry.max_capacity:
                    sm_create = ScheduleMemberCreate(
                        schedule_id=new_schedule_entry.schedule_id,
                        member_id=member_data['member_id'],
                        status=ScheduleMemberStatus.assigned
                    )
                    crud_training.add_member_to_schedule_entry(db, sm_create)
                    assigned_count += 1
                else:
                    break

            if assigned_count < new_schedule_entry.max_capacity:
                for member_data in available_members:
                    if assigned_count < new_schedule_entry.max_capacity:
                         # Avoid double booking a member at the exact same time slot if they had multiple preferences
                        already_booked = db.query(ScheduleMember).join(WeeklySchedule)\
                            .filter(ScheduleMember.member_id == member_data['member_id'],
                                    WeeklySchedule.week_start_date == target_week_start_date,
                                    WeeklySchedule.day_of_week == day_of_week,
                                    WeeklySchedule.start_time == start_time).first()
                        if not already_booked:
                            sm_create = ScheduleMemberCreate(
                                schedule_id=new_schedule_entry.schedule_id,
                                member_id=member_data['member_id'],
                                status=ScheduleMemberStatus.assigned
                            )
                            crud_training.add_member_to_schedule_entry(db, sm_create)
                            assigned_count += 1
                    else:
                        break
            print(f"Assigned {assigned_count} members to schedule ID {new_schedule_entry.schedule_id}")

        db.commit() # Commit all changes for the week
        print("Initial scheduling complete.")
    except Exception as e:
        db.rollback()
        print(f"Error during initial scheduling: {e}")
    finally:
        db.close()

def run_final_scheduling_adjustments():
    """
    Runs on Saturday 00:00.
    Adjusts the schedule based on member cancellations/changes and tries to optimize.
    This is where adapting Meetly's DFS/BFS for augmenting paths would be beneficial.
    For now, this will be a simpler version focusing on filling gaps from cancellations.
    """
    db: Session = SessionLocal()
    try:
        manager_user_id = 1 # Placeholder
        manager_user = db.query(User).filter(User.user_type == 'manager').first()
        if manager_user:
            manager_user_id = manager_user.user_id

        target_week_start_date = get_next_week_start_date() # Schedule for the upcoming week
        print(f"Running final scheduling adjustments for week starting: {target_week_start_date}")

        # 1. Identify sessions with cancellations or low occupancy
        # For simplicity, let's say we re-evaluate all 'Scheduled' sessions

        all_scheduled_sessions = db.query(WeeklySchedule).filter(
            WeeklySchedule.week_start_date == target_week_start_date,
            WeeklySchedule.status == ScheduleStatus.scheduled
        ).all()

        for session in all_scheduled_sessions:
            current_occupancy = db.query(ScheduleMember).filter(
                ScheduleMember.schedule_id == session.schedule_id,
                ScheduleMember.status.notin_([ScheduleMemberStatus.cancelled]) # Count non-cancelled
            ).count()

            available_spots = session.max_capacity - current_occupancy

            if available_spots > 0:
                print(f"Session {session.schedule_id} has {available_spots} available spots. Trying to fill.")

                # Find members who preferred this slot but weren't assigned, or marked as 'Available'
                # and are not already in ANY session at this specific time.

                # Get all members already scheduled at this exact time slot to avoid double booking
                members_already_in_any_session_at_this_time = db.query(ScheduleMember.member_id)\
                    .join(WeeklySchedule, WeeklySchedule.schedule_id == ScheduleMember.schedule_id)\
                    .filter(
                        WeeklySchedule.week_start_date == target_week_start_date,
                        WeeklySchedule.day_of_week == session.day_of_week,
                        WeeklySchedule.start_time == session.start_time,
                        ScheduleMember.status.notin_([ScheduleMemberStatus.cancelled])
                    ).distinct().all()

                member_ids_already_booked = [m_id for m_id, in members_already_in_any_session_at_this_time]

                potential_candidates = db.query(TrainingPreference)\
                    .filter(
                        TrainingPreference.week_start_date == target_week_start_date,
                        TrainingPreference.day_of_week == session.day_of_week,
                        TrainingPreference.start_time == session.start_time,
                        TrainingPreference.end_time == session.end_time,
                        TrainingPreference.preference_type.in_([PreferenceType.preferred, PreferenceType.available]),
                        TrainingPreference.member_id.notin_(member_ids_already_booked) # Not already in any session at this time
                    )\
                    .order_by(TrainingPreference.preference_type.desc()) # 'Preferred' first
                    .limit(available_spots * 2) # Fetch more candidates than spots to have options
                    .all()

                newly_assigned_count = 0
                for candidate_pref in potential_candidates:
                    if newly_assigned_count >= available_spots:
                        break

                    # Check if this member is already in THIS specific session (shouldn't happen if logic is correct above)
                    is_already_in_this_session = db.query(ScheduleMember).filter(
                        ScheduleMember.schedule_id == session.schedule_id,
                        ScheduleMember.member_id == candidate_pref.member_id,
                        ScheduleMember.status.notin_([ScheduleMemberStatus.cancelled])
                    ).count() > 0

                    if not is_already_in_this_session:
                        sm_create = ScheduleMemberCreate(
                            schedule_id=session.schedule_id,
                            member_id=candidate_pref.member_id,
                            status=ScheduleMemberStatus.assigned
                        )
                        crud_training.add_member_to_schedule_entry(db, sm_create)
                        newly_assigned_count += 1
                        print(f"Added member {candidate_pref.member_id} to session {session.schedule_id}")

        # TODO: Implement logic for handling member change requests using an adapted DFS/BFS
        # This would involve:
        # 1. A table for `TrainingChangeRequest`.
        # 2. Building a graph of (Member <-> ScheduledSession) with preferences as edge weights/types.
        # 3. For each change request, try to find an augmenting path.

        db.commit()
        print("Final scheduling adjustments complete.")
    except Exception as e:
        db.rollback()
        print(f"Error during final scheduling adjustments: {e}")
    finally:
        db.close()

```

**File: `backend/api.py`** (Add APScheduler)

```python
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
```

_Note on APScheduler_: Managing database sessions within scheduled jobs requires care. `SessionLocal()` should be called inside the job function.

**File: `backend/routes/training.py`** (Significant updates for new features)

```python
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models.training import TrainingPlan, Exercise # Added Exercise
from backend.database.schemas.training import (
    TrainingPlanCreate,
    TrainingPlanResponse,
    TrainingPlanUpdate,
    TrainingPreferenceCreate, TrainingPreferenceUpdate, TrainingPreferenceResponse,
    WeeklyScheduleResponse, # Keep generic, details can be derived or added in CRUD
    LiveSessionCreate, LiveSessionResponse, LiveSessionUpdate,
    LiveSessionExerciseCreate, LiveSessionExerciseUpdate, LiveSessionExercise as LiveSessionExerciseSchema, # Renamed for clarity
    ScheduleMemberStatus, DayOfWeek as DayOfWeekEnum, # Import enums
    TrainingCycleResponse # Placeholder for future
)
from backend.database.schemas.user import UserResponse # For user details in responses

from typing import List, Optional
from ..database.crud import training as crud
from ..auth import get_current_user_auth_info # Use the renamed function
from datetime import datetime, date, time

router = APIRouter(tags=["Training System"]) # Combined tag

# === Training Plans (Existing, minor adjustments if needed) ===
@router.get("/training-plans", response_model=List[TrainingPlanResponse])
def get_all_training_plans(db: Session = Depends(get_db)):
    return db.query(TrainingPlan).all()

@router.get("/training-plans/{plan_id}", response_model=TrainingPlanResponse)
def get_training_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(TrainingPlan).filter(TrainingPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Training plan not found")
    return plan

@router.post("/training-plans", response_model=TrainingPlanResponse, status_code=status.HTTP_201_CREATED)
def create_training_plan(plan_data: TrainingPlanCreate, db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user_auth_info)):
    # Add authorization if needed, e.g., only trainers/managers can create
    if user_auth.get("user_type") not in ["trainer", "manager"]:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create training plans")
    new_plan = TrainingPlan(**plan_data.dict())
    # If plan_data expects created_by from auth:
    # new_plan.created_by = user_auth.get("trainer_id") # if a trainer is creating
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

# === Training Preferences ===
@router.post("/training-preferences", response_model=TrainingPreferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_member_preference(
    preference_in: TrainingPreferenceCreate,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    if user_auth.get("user_type") != "member" or user_auth.get("member_id") != preference_in.member_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Logic to check if it's Thursday (can be helper function)
    if datetime.today().weekday() != 3: # Monday is 0 and Sunday is 6
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Preferences can only be set/updated on Thursdays.")

    return crud.create_training_preference(db, preference_in=preference_in)

@router.get("/training-preferences/member/week/{week_start_iso_date}", response_model=List[TrainingPreferenceResponse])
async def get_member_preferences(
    week_start_iso_date: str,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        week_start_date = date.fromisoformat(week_start_iso_date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD.")

    return crud.get_member_preferences_for_week(db, member_id, week_start_date)

@router.delete("/training-preferences/{preference_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member_preference(
    preference_id: int,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    if datetime.today().weekday() != 3:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Preferences can only be deleted on Thursdays.")

    pref = crud.get_training_preference(db, preference_id)
    if not pref:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preference not found")
    if user_auth.get("user_type") != "member" or user_auth.get("member_id") != pref.member_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this preference")

    crud.delete_training_preference(db, preference_id)
    return


# === Weekly Schedule ===
@router.get("/weekly-schedule/member/{week_start_iso_date}", response_model=List[WeeklyScheduleResponse])
async def get_member_weekly_schedule(
    week_start_iso_date: str,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        week_start_date = date.fromisoformat(week_start_iso_date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format for week_start_date.")

    schedules = crud.get_member_schedules_for_week(db, member_id, week_start_date)
    return schedules

@router.get("/weekly-schedule/trainer/{week_start_iso_date}", response_model=List[WeeklyScheduleResponse])
async def get_trainer_weekly_schedule(
    week_start_iso_date: str,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    trainer_id = user_auth.get("trainer_id")
    if not trainer_id or user_auth.get("user_type") != "trainer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        week_start_date = date.fromisoformat(week_start_iso_date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format.")
    return crud.get_trainer_schedules_for_week(db, trainer_id, week_start_date)


@router.get("/weekly-schedule/manager/{week_start_iso_date}", response_model=List[WeeklyScheduleResponse])
async def get_manager_weekly_schedule( # Manager sees all
    week_start_iso_date: str,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    if user_auth.get("user_type") != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        week_start_date = date.fromisoformat(week_start_iso_date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format.")
    return crud.get_schedules_for_week(db, week_start_date)


@router.put("/weekly-schedule/member/{schedule_member_id}/status", response_model=ScheduleMemberCreate) # Using Create as it matches fields
async def update_member_schedule_status(
    schedule_member_id: int,
    new_status: ScheduleMemberStatus, # Pass status as a query parameter or in body
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    # Check if user is the member themselves or a manager/trainer involved
    sm = db.query(crud.ScheduleMember).filter(crud.ScheduleMember.id == schedule_member_id).first()
    if not sm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled item not found")

    is_member_self = user_auth.get("user_type") == "member" and user_auth.get("member_id") == sm.member_id
    # TODO: Add trainer/manager authorization check if they are allowed to change status

    if not is_member_self: # Add other auth checks here
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to change this status")

    # Add logic for 24-hour change window (Friday to Saturday)
    # Example: if datetime.now() > (schedule_publication_time + timedelta(hours=24)) and new_status == ScheduleMemberStatus.cancelled :
    # raise HTTPException(status_code=403, detail="Change/cancellation window closed")

    updated_sm = crud.update_schedule_member_status(db, schedule_member_id, new_status)
    if not updated_sm:
        raise HTTPException(status_code=500, detail="Failed to update status")
    return updated_sm


# === Live Training Sessions ===
@router.post("/live-sessions", response_model=LiveSessionResponse)
async def start_live_training_session(
    session_create: LiveSessionCreate, # Contains schedule_id
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    if user_auth.get("user_type") not in ["trainer", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only trainers or managers can start sessions.")

    # Verify the trainer/manager is associated with the schedule_id if needed
    schedule_entry = crud.get_weekly_schedule_by_id(db, session_create.schedule_id)
    if not schedule_entry:
        raise HTTPException(status_code=404, detail="Scheduled session not found.")
    if user_auth.get("user_type") == "trainer" and schedule_entry.trainer_id != user_auth.get("trainer_id"):
        raise HTTPException(status_code=403, detail="Trainer not assigned to this schedule.")

    live_session = crud.create_live_session(db, schedule_id=session_create.schedule_id, notes=session_create.notes)
    return live_session

@router.put("/live-sessions/{live_session_id}/end", response_model=LiveSessionResponse)
async def end_live_training_session(
    live_session_id: int,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    if user_auth.get("user_type") not in ["trainer", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only trainers or managers can end sessions.")

    live_session = crud.get_live_session_by_id(db, live_session_id)
    if not live_session:
        raise HTTPException(status_code=404, detail="Live session not found.")
    # Add auth check: if trainer, ensure it's their session

    return crud.update_live_session_status(db, live_session_id, status=ScheduleStatus.completed, end_time=datetime.utcnow())


@router.get("/live-sessions/active/member", response_model=Optional[LiveSessionResponse])
async def get_member_active_live_session(db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user_auth_info)):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member": return None # Or raise 403
    return crud.get_active_live_session_for_member(db, member_id)

@router.get("/live-sessions/active/trainer", response_model=Optional[LiveSessionResponse])
async def get_trainer_active_live_session(db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user_auth_info)):
    trainer_id = user_auth.get("trainer_id")
    if not trainer_id or user_auth.get("user_type") != "trainer": return None
    return crud.get_active_live_session_for_trainer(db, trainer_id)

@router.get("/live-sessions/active/manager", response_model=List[LiveSessionResponse])
async def get_manager_all_active_live_sessions(db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user_auth_info)):
    if user_auth.get("user_type") != "manager": return []
    return crud.get_all_active_live_sessions(db)


@router.get("/live-sessions/{live_session_id}/exercises/member", response_model=List[LiveSessionExerciseSchema])
async def get_live_session_exercises(
    live_session_id: int,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    exercises_data = crud.get_live_session_exercises_for_member(db, live_session_id, member_id)
    # The CRUD function now joins Exercise and adds columns. Schema needs to match.
    # Let's assume LiveSessionExerciseSchema includes these fields.

    # If the schema doesn't directly match the joined result, map it here:
    response_data = []
    for row in exercises_data: # Assuming row is a tuple/object with attributes
        live_exercise_part = row.LiveSessionExercise # if query returns models
        exercise_part = row # if query returns joined columns
        response_data.append(LiveSessionExerciseSchema(
            id=live_exercise_part.id,
            live_session_id=live_exercise_part.live_session_id,
            member_id=live_exercise_part.member_id,
            exercise_id=live_exercise_part.exercise_id,
            sets_completed=live_exercise_part.sets_completed,
            actual_reps=live_exercise_part.actual_reps,
            weight_used=live_exercise_part.weight_used,
            comments=live_exercise_part.comments,
            completed=live_exercise_part.completed,
            completed_at=live_exercise_part.completed_at,
            created_at=live_exercise_part.created_at,
            updated_at=live_exercise_part.updated_at,
            # Add fields from Exercise model if schema expects them
            # exercise_name=exercise_part.exercise_name,
            # instructions=exercise_part.instructions,
            # ...
        ))
    return response_data


@router.post("/live-sessions/exercises", response_model=LiveSessionExerciseSchema)
async def upsert_live_exercise_progress(
    exercise_progress: LiveSessionExerciseCreate,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member" or exercise_progress.member_id != member_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Check if live_session is active and belongs to member
    live_session = crud.get_live_session_by_id(db, exercise_progress.live_session_id)
    if not live_session or live_session.status not in [LiveSessionStatus.started, LiveSessionStatus.in_progress]:
        raise HTTPException(status_code=400, detail="Live session is not active or does not exist.")
    # Further check if member is part of this live session

    return crud.add_or_update_live_session_exercise(db, exercise_progress)

@router.put("/live-sessions/exercises/{live_session_exercise_id}/complete", response_model=LiveSessionExerciseSchema)
async def mark_exercise_complete(
    live_session_exercise_id: int, # This should be the ID of LiveSessionExercise record
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Fetch the live session exercise record
    lse_record = db.query(crud.LiveSessionExercise).filter(crud.LiveSessionExercise.id == live_session_exercise_id).first()
    if not lse_record:
        raise HTTPException(status_code=404, detail="Exercise record not found.")
    if lse_record.member_id != member_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this exercise.")

    return crud.complete_live_session_exercise(db, lse_record.live_session_id, member_id, lse_record.exercise_id)

# === Training History ===
@router.get("/training-history/member", response_model=List[LiveSessionExerciseSchema]) # Adjust response model as needed
async def get_my_training_history(
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    history = crud.get_member_training_history(db, member_id)
    # Map to schema, similar to get_live_session_exercises
    response_data = []
    for row in history:
        live_exercise_part = row.LiveSessionExercise
        response_data.append(LiveSessionExerciseSchema(
            id=live_exercise_part.id,
            live_session_id=live_exercise_part.live_session_id,
            member_id=live_exercise_part.member_id,
            exercise_id=live_exercise_part.exercise_id,
            sets_completed=live_exercise_part.sets_completed,
            actual_reps=live_exercise_part.actual_reps,
            weight_used=live_exercise_part.weight_used,
            comments=live_exercise_part.comments,
            completed=live_exercise_part.completed,
            completed_at=live_exercise_part.completed_at,
            created_at=live_exercise_part.created_at,
            updated_at=live_exercise_part.updated_at,
            # Add joined fields if schema expects them
            # session_start_time=row.session_start_time,
            # session_day=row.session_day,
            # exercise_name=row.exercise_name
        ))
    return response_data


# Placeholder for trainers/managers to view member progress in a live session
@router.get("/live-sessions/{live_session_id}/all-members-progress", response_model=List[dict]) # Define a proper schema
async def get_all_members_progress_for_session(
    live_session_id: int,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    if user_auth.get("user_type") not in ["trainer", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Auth check: if trainer, ensure it's their session
    live_session = crud.get_live_session_by_id(db, live_session_id)
    if not live_session:
        raise HTTPException(status_code=404, detail="Live session not found.")

    if user_auth.get("user_type") == "trainer":
        schedule = crud.get_weekly_schedule_by_id(db, live_session.schedule_id)
        if not schedule or schedule.trainer_id != user_auth.get("trainer_id"):
            raise HTTPException(status_code=403, detail="Trainer not authorized for this session's progress.")

    return crud.get_live_session_exercises_for_trainer_view(db, live_session_id)

```

**Phase 2: Frontend Implementation**

**Helper function for API calls in frontend pages:**
Create a helper in `frontend/utils.py` (new file) or directly in pages.

```python
# frontend/utils.py (New file)
import httpx
from nicegui import ui
import json
from frontend.config import API_HOST, API_PORT

async def api_call(method: str, endpoint: str, payload: Optional[dict] = None, params: Optional[dict] = None) -> Optional[dict]:
    """Helper function to make authenticated API calls."""
    try:
        token = await ui.run_javascript("localStorage.getItem('token')")
        if not token:
            ui.notify("Authentication token not found. Please log in.", color='negative')
            # ui.navigate.to(f"http://{API_HOST}:{API_PORT}/login") # Careful with navigation from non-page context
            return None

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"http://{API_HOST}:{API_PORT}/api{endpoint}" # Assuming /api prefix

        async with httpx.AsyncClient(timeout=10.0) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=payload)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=payload)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers, params=params)
            else:
                ui.notify(f"Unsupported HTTP method: {method}", color='negative')
                return None

        if 200 <= response.status_code < 300:
            if response.status_code == 204: # No content
                return {"success": True}
            return response.json()
        else:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get("detail", response.text)
            except: # json.JSONDecodeError
                error_detail = response.text
            ui.notify(f"API Error ({response.status_code}): {error_detail}", color='negative', multi_line=True, close_button='OK')
            return None

    except httpx.RequestError as e:
        ui.notify(f"Request failed: {e}", color='negative')
        return None
    except Exception as e:
        ui.notify(f"An unexpected error occurred: {e}", color='negative')
        return None

async def get_current_user_details():
    """Fetches user details from /me endpoint."""
    return await api_call("GET", "/me")

```

**File: `frontend/pages/home_page.py`** (Update `get_current_user` and Live Training button)

```python
from nicegui import ui, app
from frontend.config import API_HOST, API_PORT
from frontend.utils import api_call, get_current_user_details # Import new utils
import asyncio # For sleep

async def home_page():
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    ui.query('.nicegui-content').classes('items-center')

    user = await get_current_user_details() # Use the new utility

    if user and user.get("first_name") == "temp_first_name":
        ui.navigate.to('/full-details')
        return

    print("DEBUG: home_page.py User:", user)

    # Navbar
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
        with ui.row().classes('gap-4 items-center'): # Added items-center
            ui.button('Home', on_click=lambda: ui.navigate.to('/')).props('flat color=white')
            ui.button('Working Hours', on_click=lambda: ui.navigate.to('/work-hours')).props('flat color=white')
            ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).props('flat color=white')
            ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).props('flat color=white')
            ui.button('Weekly Schedule', on_click=lambda: ui.navigate.to('/weekly-schedule')).props('flat color=white')

            is_thursday = datetime.date.today().weekday() == 3 # Thursday
            if user and user.get("user_type") == "member" and is_thursday:
                 ui.button('Set Preferences', on_click=lambda: ui.navigate.to('/training-preferences')).props('flat color=white icon=event')

            # Check for active live session (member or trainer)
            live_session_button_placeholder = ui.row() # Placeholder for the button

            async def check_and_show_live_button():
                live_session_button_placeholder.clear()
                active_session = None
                if user:
                    if user.get("user_type") == "member":
                        active_session = await api_call("GET", "/live-sessions/active/member")
                    elif user.get("user_type") == "trainer":
                        active_session = await api_call("GET", "/live-sessions/active/trainer")
                    # Managers might see a different kind of live overview, not a single "Live Training" button for themselves.

                if active_session: # active_session will be the session object or None
                    with live_session_button_placeholder:
                        ui.button('Live Training', on_click=lambda: ui.navigate.to('/live-dashboard')).props('flat color=red icon=fitness_center')

            await check_and_show_live_button() # Initial check
            # ui.timer(30.0, check_and_show_live_button, once=False) # Optionally, periodically check

            if user:
                with ui.dropdown_button(f'👤 {user.get("first_name", "Account")}', auto_close=True).props('flat color=white'):
                    ui.menu_item('My Profile', on_click=lambda: ui.navigate.to('/myprofile'))
                    if user.get("user_type") == "member":
                        ui.menu_item('My Bookings (Classes)', on_click=lambda: ui.navigate.to('/mybookings'))
                        ui.menu_item('My Training History', on_click=lambda: ui.navigate.to('/mytrainingplans'))
                    ui.menu_item('Logout', on_click=logout)
            else:
                ui.button('Login', on_click=login).props('flat color=white')

    # Main content (as before)
    with ui.card().classes('w-full p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg'):
        if not user:
            ui.label('Welcome to Gym Manager').classes('text-4xl font-bold text-center mb-4 text-blue-300')
            ui.label('Your complete solution for managing gym activities, classes, and training plans.').classes('text-lg text-center mb-6 text-gray-300')
            ui.button('Login/Register', on_click=login).classes('w-1/2 bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors mb-6')
        else:
            ui.label(f'Welcome back, {user.get("first_name", "User")}!').classes('text-2xl font-bold text-center mb-6 text-blue-300')

        with ui.row().classes('gap-8 justify-center mt-6'):
            # Columns as before
            with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md items-center'):
                ui.icon('schedule', size='lg').classes('text-cyan-400 mb-2')
                ui.label('Work Hours').classes('text-xl font-bold text-center mb-2 text-blue-300')
                ui.button('View Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600')

            with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md items-center'):
                ui.icon('groups', size='lg').classes('text-cyan-400 mb-2')
                ui.label('Classes').classes('text-xl font-bold text-center mb-2 text-blue-300')
                ui.button('View Classes', on_click=lambda: ui.navigate.to('/classes')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600')

            with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md items-center'):
                ui.icon('fitness_center', size='lg').classes('text-cyan-400 mb-2')
                ui.label('Training Plans').classes('text-xl font-bold text-center mb-2 text-blue-300')
                ui.button('View Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600')

def login():
    # The /login route on backend redirects to Auth0
    ui.navigate.to(f"http://{API_HOST}:{API_PORT}/login", new_tab=False)

def logout():
    # Clear local token and redirect to backend logout which handles Auth0
    ui.run_javascript("localStorage.removeItem('token'); localStorage.removeItem('user_info');")
    ui.navigate.to(f"http://{API_HOST}:{API_PORT}/logout", new_tab=False)
    # A full page reload might be needed after logout to clear state
    # ui.navigate.to('/', new_tab=False, force_reload=True) # Consider after Auth0 redirect

```

**File: `frontend/pages/training_preferences.py`**
This page needs substantial changes to interact with the new backend.

```python
from nicegui import ui
import datetime
from frontend.config import API_HOST, API_PORT
from frontend.utils import api_call, get_current_user_details
import asyncio

async def display_training_preferences():
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    ui.query('.nicegui-content').classes('items-center')

    user = await get_current_user_details()
    if not user or user.get("user_type") != "member":
        ui.label("You must be a logged-in member to set preferences.").classes('text-xl m-auto')
        if not user: ui.button("Login", on_click=lambda: ui.navigate.to(f"http://{API_HOST}:{API_PORT}/login"))
        return

    # --- Navbar (simplified for brevity, reuse from home_page.py logic) ---
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold').on('click', lambda: ui.navigate.to('/'))
        # ... (add other nav buttons) ...

    # --- Main Content ---
    with ui.card().classes('w-full max-w-4xl p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-4'):
        ui.label('Weekly Training Preferences').classes('text-3xl font-bold text-center mb-6 text-blue-300')

        preferences_container = ui.column().classes('w-full gap-4')

        # State for selected week start date
        # Calculate next week's Sunday
        today = datetime.date.today()
        days_until_next_sunday = (6 - today.weekday() + 7) % 7
        if days_until_next_sunday == 0 and today.weekday() != 6: # if today is not sunday but calculation is 0, means next sunday
            days_until_next_sunday = 7
        elif today.weekday() == 6: # if today is sunday, schedule for next sunday
             days_until_next_sunday = 7
        next_week_start_date_obj = today + datetime.timedelta(days=days_until_next_sunday)
        next_week_start_date_iso = next_week_start_date_obj.isoformat()

        async def load_and_display_preferences():
            preferences_container.clear()
            with preferences_container:
                if datetime.date.today().weekday() != 3: # Thursday
                    ui.label("Preferences can only be set/modified on Thursdays.").classes("text-warning text-lg text-center")

                ui.label(f"Setting preferences for week starting: {next_week_start_date_iso} (Sunday)").classes("text-xl mb-4 text-center")

                # Fetch existing preferences for this week
                existing_prefs_data = await api_call("GET", f"/training-preferences/member/week/{next_week_start_date_iso}")
                existing_preferences = {}
                if existing_prefs_data:
                    for p in existing_prefs_data:
                        key = (p['day_of_week'], p['start_time'])
                        existing_preferences[key] = p

                # Fetch trainers for preferred trainer dropdown
                trainers_data = await api_call("GET", "/users/trainers") # Assuming an endpoint like this exists
                trainer_options = {None: "No Preference"}
                if trainers_data:
                    for t in trainers_data: # trainers_data should be list of UserResponse with trainer_id
                        if t.get('trainer_id'): # Ensure trainer_id is present
                             trainer_options[t['trainer_id']] = f"{t['first_name']} {t['last_name']}"


                days_of_week_for_pref = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"] # Member sets for Sun-Thu
                time_slots = [f"{h:02d}:00" for h in range(8, 22)] # Example: 8 AM to 9 PM, 1-hour slots for simplicity

                with ui.tabs().classes('w-full') as tabs:
                    for day_name in days_of_week_for_pref:
                        ui.tab(day_name)

                with ui.tab_panels(tabs, value=days_of_week_for_pref[0]).classes('w-full'):
                    for day_name in days_of_week_for_pref:
                        with ui.tab_panel(day_name):
                            ui.label(day_name).classes("text-2xl font-semibold mb-2")
                            for start_hour_str in time_slots:
                                start_time_obj = datetime.datetime.strptime(start_hour_str, "%H:%M").time()
                                # Assuming 1.5 hour slots for now as in your example
                                end_time_obj = (datetime.datetime.combine(datetime.date.min, start_time_obj) + timedelta(hours=1, minutes=30)).time()

                                time_display = f"{start_time_obj.strftime('%H:%M')} - {end_time_obj.strftime('%H:%M')}"
                                current_pref_key = (day_name, start_time_obj.isoformat(timespec='seconds'))
                                current_pref_details = existing_preferences.get(current_pref_key)

                                with ui.card().classes("w-full p-3 my-1 bg-gray-800"):
                                    with ui.row().classes("w-full items-center justify-between"):
                                        ui.label(time_display).classes("text-lg")

                                        pref_type_val = current_pref_details['preference_type'] if current_pref_details else "Not Available"
                                        trainer_id_val = current_pref_details['trainer_id'] if current_pref_details else None

                                        select_pref_type = ui.select(
                                            options=["Preferred", "Available", "Not Available"],
                                            value=pref_type_val,
                                            label="Your Preference"
                                        ).props("dense outlined bg-color=white text-black").classes("w-48")

                                        select_trainer = ui.select(
                                            options=trainer_options,
                                            value=trainer_id_val,
                                            label="Preferred Trainer"
                                        ).props("dense outlined bg-color=white text-black").classes("w-48")

                                        async def handle_save_preference(day, start_t, end_t, pref_select, train_select):
                                            if datetime.date.today().weekday() != 3:
                                                ui.notify("Preferences can only be set/modified on Thursdays.", color='warning')
                                                return

                                            payload = {
                                                "member_id": user['member_id'],
                                                "week_start_date": next_week_start_date_iso,
                                                "day_of_week": day,
                                                "start_time": start_t.isoformat(timespec='seconds'),
                                                "end_time": end_t.isoformat(timespec='seconds'),
                                                "preference_type": pref_select.value,
                                                "trainer_id": train_select.value if train_select.value != "No Preference" else None
                                            }

                                            # If "Not Available" and preference exists, consider it a delete or update to Not Available
                                            # The backend POST /training-preferences handles create/update based on unique key
                                            result = await api_call("POST", "/training-preferences", payload=payload)
                                            if result:
                                                ui.notify(f"Preference for {day} {time_display} saved!", color='positive')
                                                await load_and_display_preferences() # Refresh to show updated state
                                            else:
                                                ui.notify(f"Failed to save preference.", color='negative')

                                        ui.button("Save", on_click=lambda day=day_name, st=start_time_obj, et=end_time_obj, ps=select_pref_type, ts=select_trainer: handle_save_preference(day, st, et, ps, ts)).props("color=primary")

        await load_and_display_preferences()
```

_Note on Training Preferences UI_: A grid-like interface might be more user-friendly than long lists of dropdowns per time slot. NiceGUI's `ui.aggrid` could be an option for a more advanced UI here.

**File: `frontend/pages/weekly_schedule.py`**
This page will show the schedule. Managers will have a "Generate Schedule" button if the schedule for next week isn't made yet (e.g. on Friday).

```python
from nicegui import ui
import datetime
from frontend.config import API_HOST, API_PORT
from frontend.utils import api_call, get_current_user_details
import asyncio

async def display_weekly_schedule():
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    ui.query('.nicegui-content').classes('items-center')

    user = await get_current_user_details()
    if not user:
        ui.label("Please log in to view the schedule.").classes('text-xl m-auto')
        ui.button("Login", on_click=lambda: ui.navigate.to(f"http://{API_HOST}:{API_PORT}/login"))
        return

    # --- Navbar ---
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold').on('click', lambda: ui.navigate.to('/'))
        # ... (add other nav buttons from home_page.py) ...

    # --- Main Content ---
    with ui.card().classes('w-full max-w-6xl p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-4'):
        ui.label('Weekly Training Schedule').classes('text-3xl font-bold text-center mb-6 text-blue-300')

        schedule_display_area = ui.column().classes('w-full')

        # Week selection
        today = datetime.date.today()
        current_week_start_offset = (today.weekday() - 6) % 7 # Monday=0, Sunday=6 -> make Sunday=0
        current_week_start = today - datetime.timedelta(days=current_week_start_offset)
        next_week_start = current_week_start + datetime.timedelta(weeks=1)

        week_options = {
            f"Current Week ({current_week_start.isoformat()})": current_week_start.isoformat(),
            f"Next Week ({next_week_start.isoformat()})": next_week_start.isoformat(),
        }

        selected_week_iso = ui.state(current_week_start.isoformat())

        with ui.row().classes("w-full items-center justify-between mb-4"):
            ui.select(week_options, label="Select Week", value=f"Current Week ({current_week_start.isoformat()})",
                      on_change=lambda e: setattr(selected_week_iso, 'value', week_options[e.value]) or load_schedule_for_week()).classes("w-64")

            if user.get("user_type") == "manager" and datetime.date.today().weekday() >= 4: # Friday or later
                 # For simplicity, manager can always try to generate/regenerate
                 # The backend scheduler.py handles the actual timing logic (Fri/Sat)
                 # Here, this button could trigger an ad-hoc regeneration if needed or just be illustrative
                 pass # The actual scheduling is by APScheduler. Manual trigger could be added.


        async def load_schedule_for_week():
            schedule_display_area.clear()
            week_to_load = selected_week_iso.value
            endpoint_suffix = ""
            if user.get("user_type") == "member":
                endpoint_suffix = f"/member/{week_to_load}"
            elif user.get("user_type") == "trainer":
                endpoint_suffix = f"/trainer/{week_to_load}"
            elif user.get("user_type") == "manager":
                endpoint_suffix = f"/manager/{week_to_load}"

            if not endpoint_suffix:
                with schedule_display_area: ui.label("Invalid user type for schedule viewing.")
                return

            schedule_data = await api_call("GET", f"/weekly-schedule{endpoint_suffix}")

            with schedule_display_area:
                if not schedule_data:
                    ui.label(f"No schedule found for the week of {week_to_load} for your role.").classes("text-lg text-center")
                    return

                days_in_schedule = sorted(list(set(item['day_of_week'] for item in schedule_data)), key=lambda d: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].index(d))

                with ui.tabs().classes('w-full') as tabs:
                    for day_name in days_in_schedule:
                        ui.tab(day_name)

                with ui.tab_panels(tabs, value=days_in_schedule[0] if days_in_schedule else None).classes('w-full'):
                    for day_name in days_in_schedule:
                        with ui.tab_panel(day_name):
                            day_sessions = [s for s in schedule_data if s['day_of_week'] == day_name]
                            day_sessions.sort(key=lambda s: s['start_time'])

                            if not day_sessions:
                                ui.label(f"No sessions scheduled for {day_name}.").classes("text-info")
                                continue

                            for session in day_sessions:
                                with ui.card().classes("w-full p-3 my-2 bg-gray-800"):
                                    ui.label(f"{session['start_time']} - {session['end_time']}").classes("text-xl font-semibold")
                                    ui.label(f"Hall: {session.get('hall_name', session.get('hall_id'))}") # Adapt based on response
                                    ui.label(f"Trainer: {session.get('trainer_name', session.get('trainer_id'))}")

                                    if user.get("user_type") == "member":
                                        # Display member's status for this session
                                        member_in_session = next((sm for sm in session.get('schedule_members', []) if sm['member_id'] == user.get('member_id')), None)
                                        if member_in_session:
                                            ui.label(f"Your Status: {member_in_session['status']}")
                                            # Add cancel/change buttons if within window (Fri-Sat 00:00)
                                            # publication_date = datetime.datetime.strptime(week_to_load, '%Y-%m-%d').date() - datetime.timedelta(days=2) # Assuming schedule published on Friday
                                            # if publication_date <= datetime.date.today() < publication_date + datetime.timedelta(days=1) \
                                            #    and member_in_session['status'] not in ['Cancelled', 'Attended', 'No Show']:
                                            #    ui.button("Cancel Training", on_click=lambda s_id=member_in_session['id']: cancel_my_training(s_id)).props("color=negative dense")

                                    elif user.get("user_type") in ["trainer", "manager"]:
                                        ui.label(f"Capacity: {len(session.get('schedule_members',[]))} / {session['max_capacity']}")
                                        with ui.expansion("View Members"):
                                            members_in_session = session.get('schedule_members', [])
                                            if members_in_session:
                                                for sm_detail in members_in_session:
                                                    # Need member names here - backend should provide
                                                    ui.label(f"Member ID: {sm_detail['member_id']} - Status: {sm_detail['status']}")
                                            else:
                                                ui.label("No members assigned yet.")

        async def cancel_my_training(schedule_member_id):
            # Ensure it's within the 24-hour cancellation window after schedule publication (Friday X to Saturday X)
            # For simplicity, check if it's Friday or Saturday morning before the final reschedule.
            today = datetime.date.today()
            # This logic needs refinement based on exact publication time and deadline.
            # if not (today.weekday() == 4 or (today.weekday() == 5 and datetime.datetime.now().hour < 0)): # Friday, or Sat before midnight
            #     ui.notify("Cancellation/change window is closed.", color='warning')
            #     return

            result = await api_call("PUT", f"/weekly-schedule/member/{schedule_member_id}/status?new_status=Cancelled")
            if result:
                ui.notify("Training cancelled successfully.", color='positive')
                await load_schedule_for_week()
            else:
                ui.notify("Failed to cancel training.", color='negative')

        await load_schedule_for_week()
```

**File: `frontend/pages/live_dashboard.py`**
This page will display live training information.

```python
from nicegui import ui
import datetime
from frontend.config import API_HOST, API_PORT
from frontend.utils import api_call, get_current_user_details
import asyncio
import json

async def display_live_dashboard():
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    ui.query('.nicegui-content').classes('items-center')

    user = await get_current_user_details()
    if not user:
        ui.label("Please log in.").classes('text-xl m-auto')
        return

    # --- Navbar ---
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold').on('click', lambda: ui.navigate.to('/'))
        # ... (add other nav buttons) ...

    dashboard_content_area = ui.column().classes('w-full max-w-5xl p-4 mt-4')

    async def load_live_data():
        dashboard_content_area.clear()
        with dashboard_content_area:
            ui.label('Live Training Dashboard').classes('text-3xl font-bold text-center mb-6 text-blue-300')

            live_session_data = None
            user_type = user.get("user_type")

            if user_type == "member":
                live_session_data = await api_call("GET", "/live-sessions/active/member")
                if live_session_data:
                    await member_live_view(live_session_data)
                else:
                    ui.label("You do not have an active training session right now.").classes("text-lg text-center")

            elif user_type == "trainer":
                live_session_data = await api_call("GET", "/live-sessions/active/trainer")
                if live_session_data:
                    await trainer_live_view(live_session_data)
                else:
                    ui.label("You do not have an active training session to manage right now.").classes("text-lg text-center")

            elif user_type == "manager":
                # Manager view might show a list of all active sessions
                all_active_sessions = await api_call("GET", "/live-sessions/active/manager")
                if all_active_sessions:
                    await manager_live_overview(all_active_sessions)
                else:
                    ui.label("No active training sessions in the gym currently.").classes("text-lg text-center")

            if not live_session_data and user_type != "manager": # If no specific session for member/trainer
                 if user_type == "member":
                    ui.button("View My Weekly Schedule", on_click=lambda: ui.navigate.to("/weekly-schedule")).props("color=primary outline")
                 elif user_type == "trainer":
                    ui.button("View Your Weekly Schedule", on_click=lambda: ui.navigate.to("/weekly-schedule")).props("color=primary outline")


    async def member_live_view(session_data):
        with ui.card().classes("w-full p-4 bg-gray-800"):
            ui.label(f"Live Session: Hall {session_data.get('hall_name', 'N/A')} with Trainer {session_data.get('trainer_name', 'N/A')}").classes("text-xl font-semibold")
            ui.label(f"Started: {datetime.datetime.fromisoformat(session_data['start_time'][:-1]).strftime('%Y-%m-%d %H:%M') if session_data.get('start_time') else 'N/A'}").classes("text-sm")

            exercises = await api_call("GET", f"/live-sessions/{session_data['live_session_id']}/exercises/member")
            if not exercises:
                ui.label("No exercises found for this session in your plan.").classes("text-info")
                return

            ui.label("Your Exercises for this Session:").classes("text-lg mt-4 mb-2")
            for ex_data in exercises: # ex_data should be LiveSessionExerciseSchema like
                with ui.card().classes("w-full p-3 my-2 bg-gray-700"):
                    exercise_name = ex_data.get('exercise_name', f"Exercise ID: {ex_data['exercise_id']}") # Get name from joined data
                    ui.label(f"{exercise_name} {'(Completed)' if ex_data.get('completed') else ''}").classes("text-lg font-medium")

                    # TODO: Display planned sets/reps (needs TrainingPlan linkage)
                    # For now, focus on actuals input

                    with ui.row().classes("items-center gap-2"):
                        sets_input = ui.number("Actual Sets", value=ex_data.get('sets_completed', 0), min=0).props("dense outlined").classes("w-24 bg-white text-black")
                        reps_input = ui.input("Actual Reps (e.g., 10,8,8)", value=ex_data.get('actual_reps', '')).props("dense outlined").classes("flex-grow bg-white text-black")
                        weight_input = ui.input("Weight (e.g., 50kg,BW)", value=ex_data.get('weight_used', '')).props("dense outlined").classes("flex-grow bg-white text-black")

                    comments_input = ui.textarea("Comments", value=ex_data.get('comments', '')).props("dense outlined rows=2").classes("w-full mt-2 bg-white text-black")

                    async def save_progress(live_sess_id, ex_id, member_id, sets, reps, weight, comments_val):
                        payload = {
                            "live_session_id": live_sess_id,
                            "member_id": member_id,
                            "exercise_id": ex_id,
                            "sets_completed": int(sets.value),
                            "actual_reps": reps.value,
                            "weight_used": weight.value,
                            "comments": comments_val.value
                        }
                        result = await api_call("POST", "/live-sessions/exercises", payload=payload)
                        if result:
                            ui.notify("Progress saved!", color='positive')
                            # Potentially refresh just this exercise's display or the whole list
                            ex_data.update(result) # Update local data for immediate reflection if schema matches
                            # Or full reload:
                            # await load_live_data()

                    async def mark_complete(live_sess_ex_id_from_db): # The ID of the LiveSessionExercise record
                        result = await api_call("PUT", f"/live-sessions/exercises/{live_sess_ex_id_from_db}/complete")
                        if result:
                             ui.notify("Exercise marked complete!", color='positive')
                             await load_live_data() # Full refresh to show checkmark

                    ui.button("Save Progress", on_click=lambda ex_id=ex_data['exercise_id'], s=sets_input, r=reps_input, w=weight_input, c=comments_input: \
                              save_progress(session_data['live_session_id'], ex_id, user['member_id'], s,r,w,c)).props("color=primary dense")

                    if not ex_data.get('completed'):
                        ui.button("Mark Complete", on_click=lambda ex_db_id=ex_data['id']: mark_complete(ex_db_id)).props("color=positive dense")

    async def trainer_live_view(session_data):
        with ui.card().classes("w-full p-4 bg-gray-800"):
            ui.label(f"Managing Live Session: Hall {session_data.get('hall_name', 'N/A')}").classes("text-xl font-semibold")
            ui.label(f"Started: {datetime.datetime.fromisoformat(session_data['start_time'][:-1]).strftime('%Y-%m-%d %H:%M') if session_data.get('start_time') else 'N/A'}").classes("text-sm mb-4")

            all_members_progress = await api_call("GET", f"/live-sessions/{session_data['live_session_id']}/all-members-progress")

            if not all_members_progress:
                ui.label("No members currently in this session or no progress logged yet.").classes("text-info")
            else:
                # Group progress by member
                members_map = {}
                for item in all_members_progress:
                    member_id = item['member_id']
                    if member_id not in members_map:
                        members_map[member_id] = {"first_name": item['first_name'], "last_name": item['last_name'], "exercises": []}
                    if item.get('exercise_id'): # If member has an exercise logged
                        members_map[member_id]['exercises'].append(item)

                for member_id, member_data in members_map.items():
                    with ui.expansion(f"{member_data['first_name']} {member_data['last_name']}'s Progress", icon="person").classes("my-2"):
                        if not member_data['exercises']:
                            ui.label("No specific exercises logged yet for this member in this session.")
                            continue
                        for ex_prog in member_data['exercises']:
                            with ui.card().classes("w-full p-2 my-1 bg-gray-700"):
                                ui.label(f"Exercise: {ex_prog.get('exercise_name', 'N/A')} {'(Completed)' if ex_prog.get('completed') else ''}")
                                ui.label(f"  Sets: {ex_prog.get('sets_completed', 'N/A')}, Reps: {ex_prog.get('actual_reps', 'N/A')}, Weight: {ex_prog.get('weight_used', 'N/A')}")

            async def end_session_action():
                result = await api_call("PUT", f"/live-sessions/{session_data['live_session_id']}/end")
                if result:
                    ui.notify("Session ended successfully.", color="positive")
                    await asyncio.sleep(1) # Give time for notify
                    ui.navigate.to("/weekly-schedule") # Or home
                else:
                    ui.notify("Failed to end session.", color="negative")

            ui.button("End This Session", on_click=end_session_action).props("color=negative").classes("mt-4")

    async def manager_live_overview(active_sessions):
        ui.label("All Active Gym Sessions").classes("text-xl font-semibold mb-2")
        if not active_sessions:
            ui.label("No sessions currently active.").classes("text-info")
            return

        for session in active_sessions:
            with ui.card().classes("w-full p-3 my-2 bg-gray-800"):
                ui.label(f"Session ID: {session['live_session_id']} - Hall: {session.get('hall_name', 'N/A')}").classes("text-lg font-medium")
                ui.label(f"Trainer: {session.get('trainer_name', 'N/A')}")
                ui.label(f"Started: {datetime.datetime.fromisoformat(session['start_time'][:-1]).strftime('%Y-%m-%d %H:%M') if session.get('start_time') else 'N/A'}")
                # Optionally, button to view details which calls trainer_live_view for that session_id
                # ui.button("View Details", on_click=lambda s_id=session['live_session_id']: view_specific_session_details(s_id))


    await load_live_data()
    # Auto-refresh timer (optional)
    # ui.timer(30.0, load_live_data, once=False) # Refresh every 30 seconds
```

**File: `frontend/pages/my_training_plans.py`** (Changed to My Training History)

```python
from nicegui import ui
from frontend.config import API_HOST, API_PORT
from frontend.utils import api_call, get_current_user_details # Use new utils
import datetime

async def mytrainingplans_page(): # Renamed to my_training_history_page conceptually
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')

    user = await get_current_user_details()
    if not user or user.get("user_type") != "member":
        ui.label('You must be a logged-in member to view training history.').classes('text-center text-red-500 m-auto')
        if not user: ui.button("Login", on_click=lambda: ui.navigate.to(f"http://{API_HOST}:{API_PORT}/login"))
        return

    # --- Navbar (simplified for brevity) ---
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold').on('click', lambda: ui.navigate.to('/'))
        # ... (add other nav buttons) ...

    with ui.card().classes('w-full max-w-4xl p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-4'):
        ui.label('My Training History').classes('text-3xl font-bold text-center mb-6 text-blue-300')

        history_data = await api_call("GET", "/training-history/member")

        if not history_data:
            ui.label('No training history found.').classes('text-center text-gray-400')
            return

        # Group history by session (live_session_id or a combination of date and time)
        sessions = {}
        for record in history_data:
            session_id = record.get('live_session_id') # Or construct a unique session identifier
            # session_start_time = record.get('session_start_time', 'Unknown Session Time') # From joined data
            # session_day = record.get('session_day', '') # From joined data

            # For robust grouping, ensure your backend /training-history/member returns distinct session info
            # For now, using live_session_id
            if session_id not in sessions:
                # Attempt to parse ISO string and format it
                start_time_str = record.get('created_at', datetime.datetime.utcnow().isoformat()) # Fallback
                try:
                    dt_obj = datetime.datetime.fromisoformat(start_time_str.replace('Z', '+00:00')) # Handle Zulu time
                    formatted_time = dt_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_time = start_time_str # Fallback if parsing fails

                sessions[session_id] = {
                    'time': formatted_time, # This should be the actual session time
                    'exercises': []
                }
            sessions[session_id]['exercises'].append(record)

        sorted_session_ids = sorted(sessions.keys(), key=lambda sid: sessions[sid]['time'], reverse=True)

        for session_id in sorted_session_ids:
            session = sessions[session_id]
            with ui.expansion(f"Session on {session['time']}", icon="event").classes("my-2 w-full"):
                with ui.card_section():
                    if not session['exercises']:
                        ui.label("No exercises recorded for this session.")
                        continue

                    for exercise_log in session['exercises']:
                        with ui.card().classes("w-full p-2 my-1 bg-gray-700"):
                            exercise_name = exercise_log.get('exercise_name', f"Exercise ID: {exercise_log['exercise_id']}")
                            ui.label(f"{exercise_name}").classes("text-lg font-medium")
                            ui.label(f"  Sets Completed: {exercise_log.get('sets_completed', 'N/A')}")
                            ui.label(f"  Actual Reps: {exercise_log.get('actual_reps', 'N/A')}")
                            ui.label(f"  Weight Used: {exercise_log.get('weight_used', 'N/A')}")
                            if exercise_log.get('comments'):
                                ui.label(f"  Comments: {exercise_log.get('comments')}")
```

**Next Steps & Considerations:**

1.  **Database Creation:** Ensure all tables (from `tables_queries.py` and `new_tables_queries.py` / models) are created in your MySQL database. Your `backend/database/__init__.py` has `create_tables()`. This needs to be called, e.g., in `backend/api.py` on startup if not managed by Alembic.
2.  **Trainer Availability:** The scheduling logic currently assumes trainers are available if not scheduled. A more robust system would have trainers define their availability blocks, similar to member preferences.
3.  **Training Plan Linkage in Live Session:** The `LiveSessionExercise` currently doesn't directly link to a `TrainingPlanDayExercise` for planned vs. actual comparison. This linkage needs to be established if you want to show "planned sets/reps" in the live dashboard. One way is to associate a `MemberSavedPlan` (or a `TrainingCycle`) with the `ScheduleMember` entry.
4.  **Error Handling & Validation:** Add more robust error handling and input validation on both frontend and backend.
5.  **Meetly Algorithm Adaptation for Rescheduling:** The `run_final_scheduling_adjustments` is basic. Adapting Meetly's DFS/BFS for finding augmenting paths to handle member change requests and optimize the schedule is a complex task requiring careful translation of its graph logic to the gym's N-to-1 session model.
6.  **UI/UX Refinements:** The UIs provided are functional. They can be significantly improved with better layouts, components (like `ui.aggrid` for schedules/preferences), and styling.
7.  **Testing:** Thoroughly test all user roles and use cases.
8.  **Security:** Ensure all backend endpoints have proper authorization checks based on user roles. The `get_current_user_auth_info` and role checks are a good start.
9.  **Configuration:** Move constants like `MIN_MEMBERS_FOR_SESSION` to a configuration file or database table.
10. **Full Details Page**: The `full_details.py` needs to correctly fetch the `user_db_id` (internal ID) from the `/me` endpoint to make the PUT request to `/users/{user_id}`. The current implementation of `/me` returns `user_db_id`.

This is a substantial amount of code and integration. Proceed step-by-step, testing each component. Good luck!
