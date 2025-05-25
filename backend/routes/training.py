from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models.training import TrainingPlan, Exercise
from backend.database.schemas.training import (
    TrainingPlanCreate,
    TrainingPlanResponse,
    TrainingPlanUpdate,
    TrainingPreferenceCreate, TrainingPreferenceUpdate, TrainingPreference as TrainingPreferenceSchema,
    WeeklySchedule as WeeklyScheduleSchema, # Response schema
    LiveSessionCreate, LiveSession as LiveSessionSchema, LiveSessionUpdate,
    LiveSessionExerciseCreate,
    LiveSessionExerciseUpdate, # This is for member logging progress
    LiveSessionExercise as LiveSessionExerciseSchema,
    ScheduleMemberStatusEnum, # Corrected from ScheduleMemberStatus
    TrainingDayOfWeekEnum,    # Corrected from DayOfWeekEnum
    PreferenceWindowStatusResponse,
    ScheduleMember, # This is the response model defined in your schemas
    ScheduleMemberUpdate, # This is the update model defined in your schemas
    LiveSessionStatusEnum, # This is the enum defined in your schemas
    PreferenceTypeEnum # For scheduler logic
)
# Removed: ScheduleMemberSchema (use ScheduleMember directly)
# Removed: DayOfWeekEnum (use TrainingDayOfWeekEnum directly)

from backend.database.schemas.user import UserResponse

from typing import List, Optional
from ..database.crud import training as crud
from ..auth import get_current_user_auth_info
from datetime import datetime, date, time, timedelta

router = APIRouter(tags=["Training System"])

# ... (TrainingPlan endpoints remain the same - ensure created_by logic is sound) ...
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
    user_type = user_auth.get("user_type")
    if user_type not in ["trainer", "manager"]:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create training plans")
    
    if user_type == "trainer" and plan_data.created_by is None:
        plan_data.created_by = user_auth.get("trainer_id")
    
    new_plan = TrainingPlan(**plan_data.dict())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan


# --- Training Preferences ---
def get_preference_window_status() -> PreferenceWindowStatusResponse:
    today = datetime.today()
    days_until_next_sunday = (6 - today.weekday() + 7) % 7
    if days_until_next_sunday == 0 and today.weekday() != 6: days_until_next_sunday = 7
    elif today.weekday() == 6: days_until_next_sunday = 7
    target_week_start_date = today.date() + timedelta(days=days_until_next_sunday)

    if today.weekday() == 3: # Thursday
        return PreferenceWindowStatusResponse(status="submission_open", target_week_start_date=target_week_start_date)
    elif today.weekday() == 4: # Friday
        return PreferenceWindowStatusResponse(status="change_open", target_week_start_date=target_week_start_date)
    else:
        return PreferenceWindowStatusResponse(status="closed", target_week_start_date=target_week_start_date)

@router.get("/training-preferences/window-status", response_model=PreferenceWindowStatusResponse)
async def check_preference_window():
    return get_preference_window_status()

@router.post("/training-preferences", response_model=TrainingPreferenceSchema, status_code=status.HTTP_201_CREATED)
async def create_or_update_member_preference(
    preference_in: TrainingPreferenceCreate,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    window_status = get_preference_window_status()
    if window_status.status != "submission_open":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Preference submission window is currently {window_status.status}.")

    if user_auth.get("user_type") != "member" or user_auth.get("member_id") != preference_in.member_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to set preferences for this member.")
    
    if preference_in.week_start_date != window_status.target_week_start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Preferences can only be set for week starting {window_status.target_week_start_date}.")

    return crud.create_training_preference(db, preference_in=preference_in)

@router.get("/training-preferences/member/week/{week_start_iso_date}", response_model=List[TrainingPreferenceSchema])
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
    window_status = get_preference_window_status()
    if window_status.status != "submission_open":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Preferences can only be deleted during submission window.")

    pref = crud.get_training_preference(db, preference_id)
    if not pref:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preference not found")
    if user_auth.get("user_type") != "member" or user_auth.get("member_id") != pref.member_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this preference")
    
    if pref.week_start_date != window_status.target_week_start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete preferences for a past or too distant future week.")

    crud.delete_training_preference(db, preference_id)
    return


# --- Weekly Schedule ---
@router.get("/weekly-schedule/member/{week_start_iso_date}", response_model=List[WeeklyScheduleSchema])
async def get_member_weekly_schedule(
    week_start_iso_date: str,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        week_start_date_obj = date.fromisoformat(week_start_iso_date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format for week_start_date.")
    
    schedules_models = crud.get_member_schedules_for_week(db, member_id, week_start_date_obj)
    response_schedules = []
    for sm_model in schedules_models:
        current_participants = len([m for m in sm_model.schedule_members if m.status != ScheduleMemberStatusEnum.cancelled])
        
        # Use .from_orm() and then supplement with joined data
        schedule_schema = WeeklyScheduleSchema.from_orm(sm_model)
        schedule_schema.hall_name = sm_model.hall.name if sm_model.hall else None
        schedule_schema.trainer_first_name = sm_model.trainer.user.first_name if sm_model.trainer and sm_model.trainer.user else None
        schedule_schema.trainer_last_name = sm_model.trainer.user.last_name if sm_model.trainer and sm_model.trainer.user else None
        schedule_schema.current_participants = current_participants
        
        # Populate nested schedule_members
        schedule_schema.schedule_members = []
        for sched_member_model in sm_model.schedule_members:
            # This assumes ScheduleMemberNested schema is appropriate
            # and User model is accessible via sched_member_model.member.user
            member_user = sched_member_model.member.user if sched_member_model.member else None
            schedule_schema.schedule_members.append({
                "member_id": sched_member_model.member_id,
                "status": sched_member_model.status,
                "member_first_name": member_user.first_name if member_user else None,
                "member_last_name": member_user.last_name if member_user else None,
            })
        response_schedules.append(schedule_schema)
    return response_schedules


@router.get("/weekly-schedule/trainer/{week_start_iso_date}", response_model=List[WeeklyScheduleSchema])
async def get_trainer_weekly_schedule(
    week_start_iso_date: str,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    trainer_id = user_auth.get("trainer_id")
    if not trainer_id or user_auth.get("user_type") != "trainer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        week_start_date_obj = date.fromisoformat(week_start_iso_date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format.")
    
    schedules_models = crud.get_trainer_schedules_for_week(db, trainer_id, week_start_date_obj)
    response_schedules = []
    for sm_model in schedules_models: # sm_model is a WeeklyScheduleModel instance
        current_participants = len([m for m in sm_model.schedule_members if m.status != ScheduleMemberStatusEnum.cancelled])
        
        schedule_schema = WeeklyScheduleSchema.from_orm(sm_model)
        schedule_schema.hall_name = sm_model.hall.name if sm_model.hall else None
        schedule_schema.trainer_first_name = sm_model.trainer.user.first_name if sm_model.trainer and sm_model.trainer.user else None
        schedule_schema.trainer_last_name = sm_model.trainer.user.last_name if sm_model.trainer and sm_model.trainer.user else None
        schedule_schema.current_participants = current_participants
        
        schedule_schema.schedule_members = []
        for sched_member_model in sm_model.schedule_members:
            member_user = sched_member_model.member.user if sched_member_model.member else None
            schedule_schema.schedule_members.append({
                "member_id": sched_member_model.member_id,
                "status": sched_member_model.status,
                "member_first_name": member_user.first_name if member_user else None,
                "member_last_name": member_user.last_name if member_user else None,
            })
        response_schedules.append(schedule_schema)
    return response_schedules


@router.get("/weekly-schedule/manager/{week_start_iso_date}", response_model=List[WeeklyScheduleSchema])
async def get_manager_weekly_schedule(
    week_start_iso_date: str,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    if user_auth.get("user_type") != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        week_start_date_obj = date.fromisoformat(week_start_iso_date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format.")

    schedules_models = crud.get_schedules_for_week(db, week_start_date_obj) # Gets all for the week
    response_schedules = []
    for sm_model in schedules_models:
        current_participants = len([m for m in sm_model.schedule_members if m.status != ScheduleMemberStatusEnum.cancelled])
        
        schedule_schema = WeeklyScheduleSchema.from_orm(sm_model)
        schedule_schema.hall_name = sm_model.hall.name if sm_model.hall else None
        schedule_schema.trainer_first_name = sm_model.trainer.user.first_name if sm_model.trainer and sm_model.trainer.user else None
        schedule_schema.trainer_last_name = sm_model.trainer.user.last_name if sm_model.trainer and sm_model.trainer.user else None
        schedule_schema.current_participants = current_participants
        
        schedule_schema.schedule_members = []
        for sched_member_model in sm_model.schedule_members:
            member_user = sched_member_model.member.user if sched_member_model.member else None
            schedule_schema.schedule_members.append({
                "member_id": sched_member_model.member_id,
                "status": sched_member_model.status,
                "member_first_name": member_user.first_name if member_user else None,
                "member_last_name": member_user.last_name if member_user else None,
            })
        response_schedules.append(schedule_schema)
    return response_schedules


@router.put("/schedule-members/{schedule_member_id}/status", response_model=ScheduleMember) # Use ScheduleMember as response
async def update_member_schedule_status(
    schedule_member_id: int,
    new_status_body: ScheduleMemberUpdate,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    new_status = new_status_body.status
    if new_status is None:
        raise HTTPException(status_code=400, detail="New status not provided.")

    sm_model = db.query(crud.ScheduleMemberModel).filter(crud.ScheduleMemberModel.id == schedule_member_id).first()
    if not sm_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled item not found")

    is_member_self = user_auth.get("user_type") == "member" and user_auth.get("member_id") == sm_model.member_id
    
    if not is_member_self: # TODO: Add manager auth checks
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to change this status")
    
    window_status = get_preference_window_status()
    if is_member_self and new_status == ScheduleMemberStatusEnum.cancelled and window_status.status != "change_open":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Cancellation/change window is currently {window_status.status}.")
    
    updated_sm = crud.update_schedule_member_status(db, schedule_member_id, new_status)
    if not updated_sm:
        raise HTTPException(status_code=500, detail="Failed to update status")
    return updated_sm # Pydantic will convert model to schema


# --- Live Training Sessions ---
@router.post("/live-sessions", response_model=LiveSessionSchema)
async def start_live_training_session(
    session_create: LiveSessionCreate,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    user_type = user_auth.get("user_type")
    if user_type not in ["trainer", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only trainers or managers can start sessions.")
    
    schedule_entry = crud.get_weekly_schedule_by_id(db, session_create.schedule_id)
    if not schedule_entry:
        raise HTTPException(status_code=404, detail="Scheduled session not found.")
    if user_type == "trainer" and schedule_entry.trainer_id != user_auth.get("trainer_id"):
        raise HTTPException(status_code=403, detail="Trainer not assigned to this schedule.")

    live_session_model = crud.create_live_session(db, schedule_id=session_create.schedule_id, notes=session_create.notes)
    
    # TODO: Populate exercises and attendance for the response schema if needed immediately
    # This might involve more CRUD calls here or eager loading in create_live_session
    ls_schema = LiveSessionSchema.from_orm(live_session_model)
    # Example of adding related data if not handled by from_orm with relationships:
    if live_session_model.schedule:
        if live_session_model.schedule.hall: ls_schema.hall_name = live_session_model.schedule.hall.name
        if live_session_model.schedule.trainer and live_session_model.schedule.trainer.user:
            ls_schema.trainer_name = f"{live_session_model.schedule.trainer.user.first_name} {live_session_model.schedule.trainer.user.last_name}"
    return ls_schema


@router.put("/live-sessions/{live_session_id}/end", response_model=LiveSessionSchema)
async def end_live_training_session(
    live_session_id: int,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    user_type = user_auth.get("user_type")
    if user_type not in ["trainer", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only trainers or managers can end sessions.")
    
    live_session = crud.get_live_session_by_id(db, live_session_id)
    if not live_session:
        raise HTTPException(status_code=404, detail="Live session not found.")
    
    if user_type == "trainer":
        schedule = crud.get_weekly_schedule_by_id(db, live_session.schedule_id)
        if not schedule or schedule.trainer_id != user_auth.get("trainer_id"):
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Trainer not authorized for this session.")
            
    updated_session = crud.update_live_session_status(db, live_session_id, status=LiveSessionStatusEnum.completed, end_time=datetime.utcnow())
    if not updated_session:
        raise HTTPException(status_code=500, detail="Failed to end session.")
    return LiveSessionSchema.from_orm(updated_session) # Adapt with joined data if needed


@router.get("/live-sessions/active/member", response_model=Optional[LiveSessionSchema])
async def get_member_active_live_session(db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user_auth_info)):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member": return None
    session_model = crud.get_active_live_session_for_member(db, member_id)
    if session_model:
        ls_schema = LiveSessionSchema.from_orm(session_model)
        if session_model.schedule:
            if session_model.schedule.hall: ls_schema.hall_name = session_model.schedule.hall.name
            if session_model.schedule.trainer and session_model.schedule.trainer.user:
                ls_schema.trainer_name = f"{session_model.schedule.trainer.user.first_name} {session_model.schedule.trainer.user.last_name}"
        # TODO: Populate ls_schema.exercises and ls_schema.attendance if needed by frontend here
        return ls_schema
    return None

@router.get("/live-sessions/active/trainer", response_model=Optional[LiveSessionSchema])
async def get_trainer_active_live_session(db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user_auth_info)):
    trainer_id = user_auth.get("trainer_id")
    if not trainer_id or user_auth.get("user_type") != "trainer": return None
    session_model = crud.get_active_live_session_for_trainer(db, trainer_id)
    if session_model:
        ls_schema = LiveSessionSchema.from_orm(session_model)
        if session_model.schedule and session_model.schedule.hall:
            ls_schema.hall_name = session_model.schedule.hall.name
        return ls_schema
    return None


@router.get("/live-sessions/active/manager", response_model=List[LiveSessionSchema])
async def get_manager_all_active_live_sessions(db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user_auth_info)):
    if user_auth.get("user_type") != "manager": return []
    sessions_models = crud.get_all_active_live_sessions(db)
    response_list = []
    for sm_model in sessions_models:
        ls_schema = LiveSessionSchema.from_orm(sm_model)
        if sm_model.schedule:
            if sm_model.schedule.hall: ls_schema.hall_name = sm_model.schedule.hall.name
            if sm_model.schedule.trainer and sm_model.schedule.trainer.user:
                ls_schema.trainer_name = f"{sm_model.schedule.trainer.user.first_name} {sm_model.schedule.trainer.user.last_name}"
        response_list.append(ls_schema)
    return response_list


@router.get("/live-sessions/{live_session_id}/exercises/member", response_model=List[LiveSessionExerciseSchema])
async def get_live_session_exercises_for_member_route(
    live_session_id: int,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    live_session = crud.get_live_session_by_id(db, live_session_id)
    if not live_session:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found.")
    
    # Check if member is part of this live session's schedule
    is_member_in_session = db.query(crud.ScheduleMemberModel)\
        .filter(crud.ScheduleMemberModel.schedule_id == live_session.schedule_id,
                crud.ScheduleMemberModel.member_id == member_id,
                crud.ScheduleMemberModel.status != ScheduleMemberStatusEnum.cancelled)\
        .first()
    if not is_member_in_session:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Member not part of this live session.")

    exercises_data_dicts = crud.get_live_session_exercises_for_member(db, live_session_id, member_id)
    return [LiveSessionExerciseSchema.parse_obj(item) for item in exercises_data_dicts]


@router.post("/live-sessions/exercises/progress", response_model=LiveSessionExerciseSchema)
async def upsert_live_exercise_progress(
    exercise_progress_in: LiveSessionExerciseUpdate,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member" or exercise_progress_in.member_id != member_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    live_session = crud.get_live_session_by_id(db, exercise_progress_in.live_session_id)
    if not live_session or live_session.status not in [LiveSessionStatusEnum.started, LiveSessionStatusEnum.in_progress]:
        raise HTTPException(status_code=400, detail="Live session is not active or does not exist.")

    updated_log_model = crud.upsert_live_session_exercise_progress(db, exercise_progress_in)
    # Fetch joined data for the response
    log_dict = crud.get_live_session_exercises_for_member(db, updated_log_model.live_session_id, updated_log_model.member_id)
    target_log_dict = next((item for item in log_dict if item['id'] == updated_log_model.id), None)
    if target_log_dict:
        return LiveSessionExerciseSchema.parse_obj(target_log_dict)
    raise HTTPException(status_code=500, detail="Failed to retrieve updated exercise log details.")


@router.put("/live-sessions/exercises/{live_session_exercise_db_id}/complete", response_model=LiveSessionExerciseSchema)
async def mark_exercise_complete(
    live_session_exercise_db_id: int, 
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    completed_log_model = crud.complete_live_session_exercise(db, live_session_exercise_db_id, member_id)
    if not completed_log_model:
        raise HTTPException(status_code=404, detail="Exercise log not found or not authorized to update.")
    
    log_dict = crud.get_live_session_exercises_for_member(db, completed_log_model.live_session_id, completed_log_model.member_id)
    target_log_dict = next((item for item in log_dict if item['id'] == completed_log_model.id), None)
    if target_log_dict:
        return LiveSessionExerciseSchema.parse_obj(target_log_dict)
    raise HTTPException(status_code=500, detail="Failed to retrieve completed exercise log details.")


# --- Training History ---
@router.get("/training-history/member", response_model=List[LiveSessionExerciseSchema])
async def get_my_training_history(
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    member_id = user_auth.get("member_id")
    if not member_id or user_auth.get("user_type") != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    history_dicts = crud.get_member_training_history(db, member_id)
    return [LiveSessionExerciseSchema.parse_obj(item) for item in history_dicts]


@router.get("/live-sessions/{live_session_id}/all-members-progress", response_model=List[dict]) # Consider a more specific schema
async def get_all_members_progress_for_session(
    live_session_id: int,
    db: Session = Depends(get_db),
    user_auth: dict = Depends(get_current_user_auth_info)
):
    user_type = user_auth.get("user_type")
    if user_type not in ["trainer", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    live_session = crud.get_live_session_by_id(db, live_session_id)
    if not live_session:
        raise HTTPException(status_code=404, detail="Live session not found.")
    
    if user_type == "trainer":
        schedule = crud.get_weekly_schedule_by_id(db, live_session.schedule_id)
        if not schedule or schedule.trainer_id != user_auth.get("trainer_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Trainer not authorized for this session's progress.")
            
    return crud.get_live_session_exercises_for_trainer_view(db, live_session_id)