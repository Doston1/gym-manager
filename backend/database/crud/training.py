from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from sqlalchemy.exc import SQLAlchemyError # For better error handling
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time, timedelta

from ..models.training import (
    TrainingPreference as TrainingPreferenceModel, # Alias model
    WeeklySchedule as WeeklyScheduleModel,
    ScheduleMember as ScheduleMemberModel,
    LiveSession as LiveSessionModel,
    LiveSessionExercise as LiveSessionExerciseModel,
    LiveSessionAttendance as LiveSessionAttendanceModel,
    TrainingCycle as TrainingCycleModel,
    Exercise
)
from ..models.user import User, Member, Trainer
from ..models.facility import Hall
from ..schemas.training import (
    TrainingPreferenceCreate,
    TrainingPreferenceUpdate,
    TrainingPreference as TrainingPreferenceSchema, # Alias schema
    WeeklyScheduleCreate,
    WeeklyScheduleUpdate,
    WeeklySchedule as WeeklyScheduleSchema,
    ScheduleMemberCreate,
    ScheduleMemberUpdate,
    ScheduleMember as ScheduleMemberSchema,
    LiveSessionCreate,
    LiveSessionUpdate,
    LiveSession as LiveSessionSchema,
    LiveSessionExerciseCreate, # This is for pre-population
    LiveSessionExerciseUpdate, # This is for member logging progress (was LiveSessionExerciseLogUpdate)
    LiveSessionExercise as LiveSessionExerciseSchema,
    # LiveSessionAttendanceCreate, # Not explicitly used yet, but keep for consistency
    # LiveSessionAttendanceUpdate,
    # TrainingCycleCreate,
    # TrainingCycleUpdate,
    ScheduleStatusEnum, # Renamed from ScheduleStatus to avoid clash
    ScheduleMemberStatusEnum, # Renamed from ScheduleMemberStatus
    LiveSessionStatusEnum, # Renamed from LiveSessionStatus
    # AttendanceStatus, # Schema uses LiveAttendanceStatusEnum
    # CycleStatus,
    TrainingDayOfWeekEnum as DayOfWeekEnum # Using the schema's DayOfWeekEnum
)
from backend.database.base import SessionLocal # For scheduler, ensure this path is correct

# --- Training Preferences ---
def get_training_preference(db: Session, preference_id: int) -> Optional[TrainingPreferenceModel]:
    return db.query(TrainingPreferenceModel).filter(TrainingPreferenceModel.preference_id == preference_id).first()

def get_member_preferences_for_week(db: Session, member_id: int, week_start_date: date) -> List[TrainingPreferenceModel]:
    return db.query(TrainingPreferenceModel).filter(
        TrainingPreferenceModel.member_id == member_id,
        TrainingPreferenceModel.week_start_date == week_start_date
    ).all()

def create_training_preference(db: Session, preference_in: TrainingPreferenceCreate) -> TrainingPreferenceModel:
    existing_preference = db.query(TrainingPreferenceModel).filter(
        TrainingPreferenceModel.member_id == preference_in.member_id,
        TrainingPreferenceModel.week_start_date == preference_in.week_start_date,
        TrainingPreferenceModel.day_of_week == preference_in.day_of_week,
        TrainingPreferenceModel.start_time == preference_in.start_time,
        TrainingPreferenceModel.end_time == preference_in.end_time
    ).first()

    if existing_preference:
        existing_preference.preference_type = preference_in.preference_type
        existing_preference.trainer_id = preference_in.trainer_id
        db_preference = existing_preference
    else:
        db_preference = TrainingPreferenceModel(**preference_in.dict())
        db.add(db_preference)
    
    db.commit()
    db.refresh(db_preference)
    return db_preference

def update_training_preference(db: Session, preference_id: int, preference_in: TrainingPreferenceUpdate) -> Optional[TrainingPreferenceModel]:
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

def get_all_preferences_for_week(db: Session, week_start_date: date) -> List[TrainingPreferenceModel]:
    return db.query(TrainingPreferenceModel).filter(TrainingPreferenceModel.week_start_date == week_start_date).all()


# --- Weekly Schedule ---
def get_weekly_schedule_by_id(db: Session, schedule_id: int) -> Optional[WeeklyScheduleModel]:
    return db.query(WeeklyScheduleModel).filter(WeeklyScheduleModel.schedule_id == schedule_id).first()

def get_schedules_for_week(db: Session, week_start_date: date, trainer_id: Optional[int] = None, hall_id: Optional[int] = None) -> List[WeeklyScheduleModel]:
    query = db.query(WeeklyScheduleModel).filter(WeeklyScheduleModel.week_start_date == week_start_date)
    if trainer_id:
        query = query.filter(WeeklyScheduleModel.trainer_id == trainer_id)
    if hall_id:
        query = query.filter(WeeklyScheduleModel.hall_id == hall_id)
    return query.order_by(WeeklyScheduleModel.day_of_week, WeeklyScheduleModel.start_time).all()

def create_weekly_schedule_entry(db: Session, schedule_in: WeeklyScheduleCreate) -> WeeklyScheduleModel:
    db_schedule = WeeklyScheduleModel(**schedule_in.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def update_weekly_schedule_entry(db: Session, schedule_id: int, schedule_in: WeeklyScheduleUpdate) -> Optional[WeeklyScheduleModel]:
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
    db.query(WeeklyScheduleModel).filter(WeeklyScheduleModel.week_start_date == week_start_date).delete()
    db.commit()

def add_member_to_schedule_entry(db: Session, schedule_member_in: ScheduleMemberCreate) -> ScheduleMemberModel:
    db_schedule_member = ScheduleMemberModel(**schedule_member_in.dict())
    db.add(db_schedule_member)
    db.commit()
    db.refresh(db_schedule_member)
    return db_schedule_member

def get_member_schedules_for_week(db: Session, member_id: int, week_start_date: date) -> List[WeeklyScheduleModel]:
    return db.query(WeeklyScheduleModel)\
        .join(ScheduleMemberModel, WeeklyScheduleModel.schedule_id == ScheduleMemberModel.schedule_id)\
        .filter(ScheduleMemberModel.member_id == member_id, WeeklyScheduleModel.week_start_date == week_start_date)\
        .options( # Eager load related data for better performance if needed by schema
            # orm.joinedload(WeeklyScheduleModel.hall),
            # orm.joinedload(WeeklyScheduleModel.trainer).joinedload(Trainer.user),
            # orm.joinedload(WeeklyScheduleModel.schedule_members)
        )\
        .order_by(WeeklyScheduleModel.day_of_week, WeeklyScheduleModel.start_time)\
        .all()

def get_trainer_schedules_for_week(db: Session, trainer_id: int, week_start_date: date) -> List[WeeklyScheduleModel]:
    return db.query(WeeklyScheduleModel)\
        .filter(WeeklyScheduleModel.trainer_id == trainer_id, WeeklyScheduleModel.week_start_date == week_start_date)\
        .order_by(WeeklyScheduleModel.day_of_week, WeeklyScheduleModel.start_time)\
        .all()
        
def get_schedule_members(db: Session, schedule_id: int) -> List[ScheduleMemberModel]:
    return db.query(ScheduleMemberModel).filter(ScheduleMemberModel.schedule_id == schedule_id).all()

def update_schedule_member_status(db: Session, schedule_member_id: int, status: ScheduleMemberStatusEnum) -> Optional[ScheduleMemberModel]:
    sm = db.query(ScheduleMemberModel).filter(ScheduleMemberModel.id == schedule_member_id).first()
    if sm:
        sm.status = status
        db.commit()
        db.refresh(sm)
    return sm

# --- Live Sessions ---
def create_live_session(db: Session, schedule_id: int, notes: Optional[str] = None) -> LiveSessionModel:
    existing_session = db.query(LiveSessionModel).filter(
        LiveSessionModel.schedule_id == schedule_id,
        LiveSessionModel.status.notin_([LiveSessionStatusEnum.completed, LiveSessionStatusEnum.cancelled])
    ).first()
    if existing_session:
        return existing_session

    db_live_session = LiveSessionModel(
        schedule_id=schedule_id, 
        status=LiveSessionStatusEnum.started,
        notes=notes
    )
    db.add(db_live_session)
    db.commit()
    db.refresh(db_live_session)
    return db_live_session

def get_live_session_by_id(db: Session, live_session_id: int) -> Optional[LiveSessionModel]:
    return db.query(LiveSessionModel).filter(LiveSessionModel.live_session_id == live_session_id).first()

def get_live_session_by_schedule_id(db: Session, schedule_id: int) -> Optional[LiveSessionModel]:
    return db.query(LiveSessionModel).filter(LiveSessionModel.schedule_id == schedule_id).order_by(LiveSessionModel.created_at.desc()).first()


def update_live_session_status(db: Session, live_session_id: int, status: LiveSessionStatusEnum, end_time: Optional[datetime] = None) -> Optional[LiveSessionModel]:
    ls = get_live_session_by_id(db, live_session_id)
    if ls:
        ls.status = status
        if end_time:
            ls.end_time = end_time
        ls.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ls)
    return ls

def get_active_live_session_for_member(db: Session, member_id: int) -> Optional[LiveSessionModel]:
    now = datetime.utcnow()
    # Ensure DayOfWeekEnum values match strftime('%A') output or map them
    # Python's strftime('%A') gives full weekday name e.g. "Sunday"
    # The DayOfWeekEnum in schemas.training should align with this.
    current_day_str = now.strftime('%A') # e.g., "Sunday"
    
    # Find the corresponding enum member
    try:
        current_day_enum = DayOfWeekEnum(current_day_str)
    except ValueError:
        # This can happen if strftime('%A') output doesn't exactly match enum members
        # Or if DayOfWeekEnum is not comprehensive (e.g. missing Friday/Saturday if your model uses them)
        print(f"Warning: Could not map '{current_day_str}' to DayOfWeekEnum for live session check.")
        return None

    return db.query(LiveSessionModel)\
        .join(WeeklyScheduleModel, LiveSessionModel.schedule_id == WeeklyScheduleModel.schedule_id)\
        .join(ScheduleMemberModel, WeeklyScheduleModel.schedule_id == ScheduleMemberModel.schedule_id)\
        .filter(ScheduleMemberModel.member_id == member_id)\
        .filter(LiveSessionModel.status.in_([LiveSessionStatusEnum.started, LiveSessionStatusEnum.in_progress]))\
        .filter(WeeklyScheduleModel.day_of_week == current_day_enum)\
        .filter(WeeklyScheduleModel.start_time <= now.time())\
        .filter(WeeklyScheduleModel.end_time >= now.time())\
        .first()

def get_active_live_session_for_trainer(db: Session, trainer_id: int) -> Optional[LiveSessionModel]:
    now = datetime.utcnow()
    current_day_str = now.strftime('%A')
    try:
        current_day_enum = DayOfWeekEnum(current_day_str)
    except ValueError:
        print(f"Warning: Could not map '{current_day_str}' to DayOfWeekEnum for live session check.")
        return None
        
    return db.query(LiveSessionModel)\
        .join(WeeklyScheduleModel, LiveSessionModel.schedule_id == WeeklyScheduleModel.schedule_id)\
        .filter(WeeklyScheduleModel.trainer_id == trainer_id)\
        .filter(LiveSessionModel.status.in_([LiveSessionStatusEnum.started, LiveSessionStatusEnum.in_progress]))\
        .filter(WeeklyScheduleModel.day_of_week == current_day_enum)\
        .filter(WeeklyScheduleModel.start_time <= now.time())\
        .filter(WeeklyScheduleModel.end_time >= now.time())\
        .first()

def get_all_active_live_sessions(db: Session) -> List[LiveSessionModel]:
    now = datetime.utcnow()
    current_day_str = now.strftime('%A')
    try:
        current_day_enum = DayOfWeekEnum(current_day_str)
    except ValueError:
        print(f"Warning: Could not map '{current_day_str}' to DayOfWeekEnum for live session check.")
        return []

    return db.query(LiveSessionModel)\
        .join(WeeklyScheduleModel, LiveSessionModel.schedule_id == WeeklyScheduleModel.schedule_id)\
        .filter(LiveSessionModel.status.in_([LiveSessionStatusEnum.started, LiveSessionStatusEnum.in_progress]))\
        .filter(WeeklyScheduleModel.day_of_week == current_day_enum)\
        .filter(WeeklyScheduleModel.start_time <= now.time())\
        .filter(WeeklyScheduleModel.end_time >= now.time())\
        .all()
        
# --- Live Session Exercises ---
# This function is for member logging/updating their progress for an exercise in a live session
def upsert_live_session_exercise_progress(db: Session, progress_in: LiveSessionExerciseUpdate) -> LiveSessionExerciseModel:
    db_exercise_log = db.query(LiveSessionExerciseModel).filter(
        LiveSessionExerciseModel.live_session_id == progress_in.live_session_id,
        LiveSessionExerciseModel.member_id == progress_in.member_id,
        LiveSessionExerciseModel.exercise_id == progress_in.exercise_id
    ).first()

    if db_exercise_log: # Update existing log
        if progress_in.sets_completed is not None:
            db_exercise_log.sets_completed = progress_in.sets_completed
        if progress_in.actual_reps is not None:
            db_exercise_log.actual_reps = progress_in.actual_reps
        if progress_in.weight_used is not None:
            db_exercise_log.weight_used = progress_in.weight_used
        if progress_in.comments is not None:
            db_exercise_log.comments = progress_in.comments
        if progress_in.completed is not None: # If 'completed' is part of the update
            db_exercise_log.completed = progress_in.completed
            if progress_in.completed and not db_exercise_log.completed_at:
                db_exercise_log.completed_at = datetime.utcnow()
            elif not progress_in.completed: # If un-completing
                 db_exercise_log.completed_at = None

        db_exercise_log.updated_at = datetime.utcnow()
    else: # Create new log entry with the progress
        # All fields from LiveSessionExerciseUpdate are needed
        db_exercise_log = LiveSessionExerciseModel(
            live_session_id=progress_in.live_session_id,
            member_id=progress_in.member_id,
            exercise_id=progress_in.exercise_id,
            sets_completed=progress_in.sets_completed,
            actual_reps=progress_in.actual_reps,
            weight_used=progress_in.weight_used,
            comments=progress_in.comments,
            completed=progress_in.completed if progress_in.completed is not None else False,
            completed_at=datetime.utcnow() if progress_in.completed else None
        )
        db.add(db_exercise_log)
    
    try:
        db.commit()
        db.refresh(db_exercise_log)
    except SQLAlchemyError as e:
        db.rollback()
        # Log error e
        raise
    return db_exercise_log

# This function is for initially adding exercises to a live session for a member (e.g., from their plan)
def add_exercise_to_live_session_for_member(db: Session, create_in: LiveSessionExerciseCreate) -> LiveSessionExerciseModel:
    # Check if it already exists to prevent duplicates if this is called multiple times
    existing = db.query(LiveSessionExerciseModel).filter(
        LiveSessionExerciseModel.live_session_id == create_in.live_session_id,
        LiveSessionExerciseModel.member_id == create_in.member_id,
        LiveSessionExerciseModel.exercise_id == create_in.exercise_id
    ).first()
    if existing:
        return existing

    db_exercise_log = LiveSessionExerciseModel(
        live_session_id=create_in.live_session_id,
        member_id=create_in.member_id,
        exercise_id=create_in.exercise_id,
        completed=False # Initially not completed
    )
    db.add(db_exercise_log)
    db.commit()
    db.refresh(db_exercise_log)
    return db_exercise_log


def complete_live_session_exercise(db: Session, live_session_exercise_id: int, member_id: int) -> Optional[LiveSessionExerciseModel]:
    # live_session_exercise_id is the ID of the LiveSessionExerciseModel record
    db_exercise_log = db.query(LiveSessionExerciseModel).filter(
        LiveSessionExerciseModel.id == live_session_exercise_id,
        LiveSessionExerciseModel.member_id == member_id # Ensure member owns this log
    ).first()
    if db_exercise_log:
        db_exercise_log.completed = True
        if not db_exercise_log.completed_at: # Set completed_at only if not already set
            db_exercise_log.completed_at = datetime.utcnow()
        db_exercise_log.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_exercise_log)
    return db_exercise_log


def get_live_session_exercises_for_member(db: Session, live_session_id: int, member_id: int) -> List[Dict[str, Any]]:
    # Querying LiveSessionExerciseModel and joining with Exercise
    results = db.query(
            LiveSessionExerciseModel, 
            Exercise.name.label("exercise_name"), 
            Exercise.instructions, 
            Exercise.image_url, 
            Exercise.primary_muscle_group
        )\
        .join(Exercise, LiveSessionExerciseModel.exercise_id == Exercise.exercise_id)\
        .filter(LiveSessionExerciseModel.live_session_id == live_session_id, LiveSessionExerciseModel.member_id == member_id)\
        .all()
    
    # Convert to list of dictionaries to match schema expectation if necessary
    # Or ensure your Pydantic schema can handle the joinedload if you use relationships
    # For direct mapping to LiveSessionExercise schema (which includes exercise_name etc.):
    data_list = []
    for lse_model, ex_name, ex_instr, ex_img, ex_muscle in results:
        data = lse_model.__dict__ # Get model fields
        data['exercise_name'] = ex_name
        data['instructions'] = ex_instr
        data['image_url'] = ex_img
        data['primary_muscle_group'] = ex_muscle
        # Remove SQLAlchemy internal state if present
        data.pop('_sa_instance_state', None)
        data_list.append(data)
    return data_list


def get_live_session_exercises_for_trainer_view(db: Session, live_session_id: int) -> List[Dict[str, Any]]:
    results = db.query(
        Member.member_id,
        User.first_name,
        User.last_name,
        Exercise.exercise_id,
        Exercise.name.label("exercise_name"),
        LiveSessionExerciseModel.id.label("live_session_exercise_id"), # ID of the log entry
        LiveSessionExerciseModel.sets_completed,
        LiveSessionExerciseModel.actual_reps,
        LiveSessionExerciseModel.weight_used,
        LiveSessionExerciseModel.completed
    ).select_from(LiveSessionModel)\
    .join(ScheduleMemberModel, ScheduleMemberModel.schedule_id == LiveSessionModel.schedule_id)\
    .join(Member, Member.member_id == ScheduleMemberModel.member_id)\
    .join(User, User.user_id == Member.user_id)\
    .outerjoin(LiveSessionExerciseModel, and_(
        LiveSessionExerciseModel.live_session_id == LiveSessionModel.live_session_id,
        LiveSessionExerciseModel.member_id == Member.member_id
    ))\
    .outerjoin(Exercise, Exercise.exercise_id == LiveSessionExerciseModel.exercise_id)\
    .filter(LiveSessionModel.live_session_id == live_session_id)\
    .all()
    
    return [row._asdict() for row in results]


def get_member_training_history(db: Session, member_id: int) -> List[Dict[str, Any]]:
    # Querying LiveSessionExerciseModel and joining with Exercise, LiveSession, WeeklySchedule
    results = db.query(
            LiveSessionExerciseModel,
            LiveSessionModel.start_time.label("session_start_time"),
            WeeklyScheduleModel.day_of_week.label("session_day"),
            Exercise.name.label("exercise_name")
        )\
        .join(LiveSessionModel, LiveSessionExerciseModel.live_session_id == LiveSessionModel.live_session_id)\
        .join(WeeklyScheduleModel, LiveSessionModel.schedule_id == WeeklyScheduleModel.schedule_id)\
        .join(Exercise, LiveSessionExerciseModel.exercise_id == Exercise.exercise_id)\
        .filter(LiveSessionExerciseModel.member_id == member_id)\
        .order_by(LiveSessionModel.start_time.desc())\
        .all()

    data_list = []
    for lse_model, sess_start, sess_day, ex_name in results:
        data = lse_model.__dict__
        data['session_start_time'] = sess_start
        data['session_day'] = sess_day.value if sess_day else None # Get enum value
        data['exercise_name'] = ex_name
        data.pop('_sa_instance_state', None)
        data_list.append(data)
    return data_list


# --- Utility for Scheduler ---
def get_trainers_available_at_slot(db: Session, week_start_date: date, day_of_week: DayOfWeekEnum, start_time: time, end_time: time) -> List[Trainer]:
    scheduled_trainers_subquery = db.query(WeeklyScheduleModel.trainer_id)\
        .filter(
            WeeklyScheduleModel.week_start_date == week_start_date,
            WeeklyScheduleModel.day_of_week == day_of_week,
            WeeklyScheduleModel.start_time < end_time, 
            WeeklyScheduleModel.end_time > start_time   
        ).subquery()

    available_trainers = db.query(Trainer)\
        .join(User, Trainer.user_id == User.user_id)\
        .filter(
            User.is_active == True,
            Trainer.trainer_id.notin_(scheduled_trainers_subquery)
        ).all()
    return available_trainers

def get_halls_available_at_slot(db: Session, week_start_date: date, day_of_week: DayOfWeekEnum, start_time: time, end_time: time) -> List[Hall]:
    scheduled_halls_subquery = db.query(WeeklyScheduleModel.hall_id)\
        .filter(
            WeeklyScheduleModel.week_start_date == week_start_date,
            WeeklyScheduleModel.day_of_week == day_of_week,
            WeeklyScheduleModel.start_time < end_time,
            WeeklyScheduleModel.end_time > start_time
        ).subquery()

    available_halls = db.query(Hall)\
        .filter(
            Hall.is_active == True,
            Hall.hall_id.notin_(scheduled_halls_subquery)
        ).all()
    return available_halls


# ===== OLD VERSION ======
# from sqlalchemy.orm import Session
# from sqlalchemy import and_, or_, func
# from typing import List, Optional, Dict, Any
# from datetime import datetime, date, time, timedelta

# from ..models.training import (
#     TrainingPreference, 
#     WeeklySchedule, 
#     ScheduleMember, 
#     LiveSession, 
#     LiveSessionExercise,
#     LiveSessionAttendance,
#     TrainingCycle
# )
# from ..schemas.training import (
#     TrainingPreferenceCreate,
#     TrainingPreferenceUpdate,
#     WeeklyScheduleCreate,
#     WeeklyScheduleUpdate,
#     ScheduleMemberCreate,
#     ScheduleMemberUpdate,
#     LiveSessionCreate,
#     LiveSessionUpdate,
#     LiveSessionExerciseCreate,
#     LiveSessionExerciseUpdate,
#     LiveSessionAttendanceCreate,
#     LiveSessionAttendanceUpdate,
#     TrainingCycleCreate,
#     TrainingCycleUpdate,
#     ScheduleStatus,
#     ScheduleMemberStatus,
#     LiveSessionStatus,
#     AttendanceStatus,
#     CycleStatus
# )


# # Training Preferences CRUD
# def get_training_preference(db: Session, preference_id: int):
#     return db.query(TrainingPreference).filter(TrainingPreference.preference_id == preference_id).first()

# def get_member_preferences(db: Session, member_id: int, week_start_date: Optional[date] = None):
#     query = db.query(TrainingPreference).filter(TrainingPreference.member_id == member_id)
#     if week_start_date:
#         query = query.filter(TrainingPreference.week_start_date == week_start_date)
#     return query.all()

# def create_training_preference(db: Session, preference: TrainingPreferenceCreate):
#     db_preference = TrainingPreference(**preference.dict())
#     db.add(db_preference)
#     db.commit()
#     db.refresh(db_preference)
#     return db_preference

# def update_training_preference(db: Session, preference_id: int, preference: TrainingPreferenceUpdate):
#     db_preference = get_training_preference(db, preference_id)
#     if db_preference is None:
#         return None
    
#     update_data = preference.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_preference, key, value)
    
#     db.commit()
#     db.refresh(db_preference)
#     return db_preference

# def delete_training_preference(db: Session, preference_id: int):
#     db_preference = get_training_preference(db, preference_id)
#     if db_preference is None:
#         return False
    
#     db.delete(db_preference)
#     db.commit()
#     return True

# # Weekly Schedule CRUD
# def get_schedule(db: Session, schedule_id: int):
#     return db.query(WeeklySchedule).filter(WeeklySchedule.schedule_id == schedule_id).first()

# def get_weekly_schedules(db: Session, week_start_date: Optional[date] = None, trainer_id: Optional[int] = None):
#     query = db.query(WeeklySchedule)
    
#     if week_start_date:
#         query = query.filter(WeeklySchedule.week_start_date == week_start_date)
    
#     if trainer_id:
#         query = query.filter(WeeklySchedule.trainer_id == trainer_id)
    
#     return query.all()

# def create_weekly_schedule(db: Session, schedule: WeeklyScheduleCreate):
#     db_schedule = WeeklySchedule(**schedule.dict(), status=ScheduleStatus.scheduled)
#     db.add(db_schedule)
#     db.commit()
#     db.refresh(db_schedule)
#     return db_schedule

# def update_weekly_schedule(db: Session, schedule_id: int, schedule: WeeklyScheduleUpdate):
#     db_schedule = get_schedule(db, schedule_id)
#     if db_schedule is None:
#         return None
    
#     update_data = schedule.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_schedule, key, value)
    
#     db.commit()
#     db.refresh(db_schedule)
#     return db_schedule

# def delete_weekly_schedule(db: Session, schedule_id: int):
#     db_schedule = get_schedule(db, schedule_id)
#     if db_schedule is None:
#         return False
    
#     db.delete(db_schedule)
#     db.commit()
#     return True

# # Schedule Members CRUD
# def get_schedule_member(db: Session, id: int):
#     return db.query(ScheduleMember).filter(ScheduleMember.id == id).first()

# def get_schedule_members(db: Session, schedule_id: int):
#     return db.query(ScheduleMember).filter(ScheduleMember.schedule_id == schedule_id).all()

# def get_member_scheduled_sessions(db: Session, member_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
#     query = db.query(WeeklySchedule).join(
#         ScheduleMember, 
#         WeeklySchedule.schedule_id == ScheduleMember.schedule_id
#     ).filter(ScheduleMember.member_id == member_id)
    
#     if start_date:
#         query = query.filter(WeeklySchedule.week_start_date >= start_date)
    
#     if end_date:
#         end_week_start = end_date - timedelta(days=end_date.weekday())
#         query = query.filter(WeeklySchedule.week_start_date <= end_week_start)
    
#     return query.all()

# def add_member_to_schedule(db: Session, schedule_member: ScheduleMemberCreate):
#     db_schedule_member = ScheduleMember(**schedule_member.dict())
#     db.add(db_schedule_member)
#     db.commit()
#     db.refresh(db_schedule_member)
#     return db_schedule_member

# def update_schedule_member(db: Session, id: int, schedule_member: ScheduleMemberUpdate):
#     db_schedule_member = get_schedule_member(db, id)
#     if db_schedule_member is None:
#         return None
    
#     update_data = schedule_member.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_schedule_member, key, value)
    
#     db.commit()
#     db.refresh(db_schedule_member)
#     return db_schedule_member

# def remove_member_from_schedule(db: Session, id: int):
#     db_schedule_member = get_schedule_member(db, id)
#     if db_schedule_member is None:
#         return False
    
#     db.delete(db_schedule_member)
#     db.commit()
#     return True

# # Live Sessions CRUD
# def get_live_session(db: Session, live_session_id: int):
#     return db.query(LiveSession).filter(LiveSession.live_session_id == live_session_id).first()

# def get_active_live_sessions(db: Session, trainer_id: Optional[int] = None):
#     query = db.query(LiveSession).join(
#         WeeklySchedule, 
#         LiveSession.schedule_id == WeeklySchedule.schedule_id
#     ).filter(
#         LiveSession.status.in_([LiveSessionStatus.started, LiveSessionStatus.in_progress])
#     )
    
#     if trainer_id:
#         query = query.filter(WeeklySchedule.trainer_id == trainer_id)
    
#     return query.all()

# def create_live_session(db: Session, live_session: LiveSessionCreate):
#     db_live_session = LiveSession(
#         **live_session.dict(),
#         start_time=datetime.now(),
#         status=LiveSessionStatus.started
#     )
#     db.add(db_live_session)
#     db.commit()
#     db.refresh(db_live_session)
#     return db_live_session

# def update_live_session(db: Session, live_session_id: int, live_session: LiveSessionUpdate):
#     db_live_session = get_live_session(db, live_session_id)
#     if db_live_session is None:
#         return None
    
#     update_data = live_session.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_live_session, key, value)
    
#     db.commit()
#     db.refresh(db_live_session)
#     return db_live_session

# def complete_live_session(db: Session, live_session_id: int):
#     db_live_session = get_live_session(db, live_session_id)
#     if db_live_session is None:
#         return None
    
#     db_live_session.status = LiveSessionStatus.completed
#     db_live_session.end_time = datetime.now()
    
#     db.commit()
#     db.refresh(db_live_session)
#     return db_live_session

# # Live Session Exercises CRUD
# def get_session_exercise(db: Session, id: int):
#     return db.query(LiveSessionExercise).filter(LiveSessionExercise.id == id).first()

# def get_session_exercises(db: Session, live_session_id: int, member_id: Optional[int] = None):
#     query = db.query(LiveSessionExercise).filter(LiveSessionExercise.live_session_id == live_session_id)
    
#     if member_id:
#         query = query.filter(LiveSessionExercise.member_id == member_id)
    
#     return query.all()

# def add_session_exercise(db: Session, exercise: LiveSessionExerciseCreate):
#     db_exercise = LiveSessionExercise(**exercise.dict(), completed=False)
#     db.add(db_exercise)
#     db.commit()
#     db.refresh(db_exercise)
#     return db_exercise

# def update_session_exercise(db: Session, id: int, exercise: LiveSessionExerciseUpdate):
#     db_exercise = get_session_exercise(db, id)
#     if db_exercise is None:
#         return None
    
#     update_data = exercise.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_exercise, key, value)
    
#     if exercise.completed:
#         db_exercise.completed_at = datetime.now()
    
#     db.commit()
#     db.refresh(db_exercise)
#     return db_exercise

# def delete_session_exercise(db: Session, id: int):
#     db_exercise = get_session_exercise(db, id)
#     if db_exercise is None:
#         return False
    
#     db.delete(db_exercise)
#     db.commit()
#     return True

# # Live Session Attendance CRUD
# def get_attendance_record(db: Session, id: int):
#     return db.query(LiveSessionAttendance).filter(LiveSessionAttendance.id == id).first()

# def get_session_attendance(db: Session, live_session_id: int):
#     return db.query(LiveSessionAttendance).filter(
#         LiveSessionAttendance.live_session_id == live_session_id
#     ).all()

# def member_check_in(db: Session, attendance: LiveSessionAttendanceCreate):
#     db_attendance = LiveSessionAttendance(
#         **attendance.dict(),
#         check_in_time=datetime.now(),
#         status=AttendanceStatus.checked_in
#     )
#     db.add(db_attendance)
#     db.commit()
#     db.refresh(db_attendance)
#     return db_attendance

# def member_check_out(db: Session, id: int, attendance: LiveSessionAttendanceUpdate):
#     db_attendance = get_attendance_record(db, id)
#     if db_attendance is None:
#         return None
    
#     update_data = attendance.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_attendance, key, value)
    
#     if attendance.status == AttendanceStatus.checked_out:
#         db_attendance.check_out_time = datetime.now()
    
#     db.commit()
#     db.refresh(db_attendance)
#     return db_attendance

# # Training Cycles CRUD
# def get_training_cycle(db: Session, cycle_id: int):
#     return db.query(TrainingCycle).filter(TrainingCycle.cycle_id == cycle_id).first()

# def get_member_training_cycles(db: Session, member_id: int, active_only: bool = False):
#     query = db.query(TrainingCycle).filter(TrainingCycle.member_id == member_id)
    
#     if active_only:
#         query = query.filter(
#             TrainingCycle.status.in_([CycleStatus.planned, CycleStatus.in_progress])
#         )
    
#     return query.order_by(TrainingCycle.start_date.desc()).all()

# def create_training_cycle(db: Session, cycle: TrainingCycleCreate):
#     db_cycle = TrainingCycle(**cycle.dict(), status=CycleStatus.planned)
#     db.add(db_cycle)
#     db.commit()
#     db.refresh(db_cycle)
#     return db_cycle

# def update_training_cycle(db: Session, cycle_id: int, cycle: TrainingCycleUpdate):
#     db_cycle = get_training_cycle(db, cycle_id)
#     if db_cycle is None:
#         return None
    
#     update_data = cycle.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_cycle, key, value)
    
#     db.commit()
#     db.refresh(db_cycle)
#     return db_cycle

# def delete_training_cycle(db: Session, cycle_id: int):
#     db_cycle = get_training_cycle(db, cycle_id)
#     if db_cycle is None:
#         return False
    
#     db.delete(db_cycle)
#     db.commit()
#     return True