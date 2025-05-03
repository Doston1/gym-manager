from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time, timedelta

from ..models.training import (
    TrainingPreference, 
    WeeklySchedule, 
    ScheduleMember, 
    LiveSession, 
    LiveSessionExercise,
    LiveSessionAttendance,
    TrainingCycle
)
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
    CycleStatus
)


# Training Preferences CRUD
def get_training_preference(db: Session, preference_id: int):
    return db.query(TrainingPreference).filter(TrainingPreference.preference_id == preference_id).first()

def get_member_preferences(db: Session, member_id: int, week_start_date: Optional[date] = None):
    query = db.query(TrainingPreference).filter(TrainingPreference.member_id == member_id)
    if week_start_date:
        query = query.filter(TrainingPreference.week_start_date == week_start_date)
    return query.all()

def create_training_preference(db: Session, preference: TrainingPreferenceCreate):
    db_preference = TrainingPreference(**preference.dict())
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

def update_training_preference(db: Session, preference_id: int, preference: TrainingPreferenceUpdate):
    db_preference = get_training_preference(db, preference_id)
    if db_preference is None:
        return None
    
    update_data = preference.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_preference, key, value)
    
    db.commit()
    db.refresh(db_preference)
    return db_preference

def delete_training_preference(db: Session, preference_id: int):
    db_preference = get_training_preference(db, preference_id)
    if db_preference is None:
        return False
    
    db.delete(db_preference)
    db.commit()
    return True

# Weekly Schedule CRUD
def get_schedule(db: Session, schedule_id: int):
    return db.query(WeeklySchedule).filter(WeeklySchedule.schedule_id == schedule_id).first()

def get_weekly_schedules(db: Session, week_start_date: Optional[date] = None, trainer_id: Optional[int] = None):
    query = db.query(WeeklySchedule)
    
    if week_start_date:
        query = query.filter(WeeklySchedule.week_start_date == week_start_date)
    
    if trainer_id:
        query = query.filter(WeeklySchedule.trainer_id == trainer_id)
    
    return query.all()

def create_weekly_schedule(db: Session, schedule: WeeklyScheduleCreate):
    db_schedule = WeeklySchedule(**schedule.dict(), status=ScheduleStatus.scheduled)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def update_weekly_schedule(db: Session, schedule_id: int, schedule: WeeklyScheduleUpdate):
    db_schedule = get_schedule(db, schedule_id)
    if db_schedule is None:
        return None
    
    update_data = schedule.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_schedule, key, value)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_weekly_schedule(db: Session, schedule_id: int):
    db_schedule = get_schedule(db, schedule_id)
    if db_schedule is None:
        return False
    
    db.delete(db_schedule)
    db.commit()
    return True

# Schedule Members CRUD
def get_schedule_member(db: Session, id: int):
    return db.query(ScheduleMember).filter(ScheduleMember.id == id).first()

def get_schedule_members(db: Session, schedule_id: int):
    return db.query(ScheduleMember).filter(ScheduleMember.schedule_id == schedule_id).all()

def get_member_scheduled_sessions(db: Session, member_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
    query = db.query(WeeklySchedule).join(
        ScheduleMember, 
        WeeklySchedule.schedule_id == ScheduleMember.schedule_id
    ).filter(ScheduleMember.member_id == member_id)
    
    if start_date:
        query = query.filter(WeeklySchedule.week_start_date >= start_date)
    
    if end_date:
        end_week_start = end_date - timedelta(days=end_date.weekday())
        query = query.filter(WeeklySchedule.week_start_date <= end_week_start)
    
    return query.all()

def add_member_to_schedule(db: Session, schedule_member: ScheduleMemberCreate):
    db_schedule_member = ScheduleMember(**schedule_member.dict())
    db.add(db_schedule_member)
    db.commit()
    db.refresh(db_schedule_member)
    return db_schedule_member

def update_schedule_member(db: Session, id: int, schedule_member: ScheduleMemberUpdate):
    db_schedule_member = get_schedule_member(db, id)
    if db_schedule_member is None:
        return None
    
    update_data = schedule_member.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_schedule_member, key, value)
    
    db.commit()
    db.refresh(db_schedule_member)
    return db_schedule_member

def remove_member_from_schedule(db: Session, id: int):
    db_schedule_member = get_schedule_member(db, id)
    if db_schedule_member is None:
        return False
    
    db.delete(db_schedule_member)
    db.commit()
    return True

# Live Sessions CRUD
def get_live_session(db: Session, live_session_id: int):
    return db.query(LiveSession).filter(LiveSession.live_session_id == live_session_id).first()

def get_active_live_sessions(db: Session, trainer_id: Optional[int] = None):
    query = db.query(LiveSession).join(
        WeeklySchedule, 
        LiveSession.schedule_id == WeeklySchedule.schedule_id
    ).filter(
        LiveSession.status.in_([LiveSessionStatus.started, LiveSessionStatus.in_progress])
    )
    
    if trainer_id:
        query = query.filter(WeeklySchedule.trainer_id == trainer_id)
    
    return query.all()

def create_live_session(db: Session, live_session: LiveSessionCreate):
    db_live_session = LiveSession(
        **live_session.dict(),
        start_time=datetime.now(),
        status=LiveSessionStatus.started
    )
    db.add(db_live_session)
    db.commit()
    db.refresh(db_live_session)
    return db_live_session

def update_live_session(db: Session, live_session_id: int, live_session: LiveSessionUpdate):
    db_live_session = get_live_session(db, live_session_id)
    if db_live_session is None:
        return None
    
    update_data = live_session.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_live_session, key, value)
    
    db.commit()
    db.refresh(db_live_session)
    return db_live_session

def complete_live_session(db: Session, live_session_id: int):
    db_live_session = get_live_session(db, live_session_id)
    if db_live_session is None:
        return None
    
    db_live_session.status = LiveSessionStatus.completed
    db_live_session.end_time = datetime.now()
    
    db.commit()
    db.refresh(db_live_session)
    return db_live_session

# Live Session Exercises CRUD
def get_session_exercise(db: Session, id: int):
    return db.query(LiveSessionExercise).filter(LiveSessionExercise.id == id).first()

def get_session_exercises(db: Session, live_session_id: int, member_id: Optional[int] = None):
    query = db.query(LiveSessionExercise).filter(LiveSessionExercise.live_session_id == live_session_id)
    
    if member_id:
        query = query.filter(LiveSessionExercise.member_id == member_id)
    
    return query.all()

def add_session_exercise(db: Session, exercise: LiveSessionExerciseCreate):
    db_exercise = LiveSessionExercise(**exercise.dict(), completed=False)
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

def update_session_exercise(db: Session, id: int, exercise: LiveSessionExerciseUpdate):
    db_exercise = get_session_exercise(db, id)
    if db_exercise is None:
        return None
    
    update_data = exercise.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_exercise, key, value)
    
    if exercise.completed:
        db_exercise.completed_at = datetime.now()
    
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

def delete_session_exercise(db: Session, id: int):
    db_exercise = get_session_exercise(db, id)
    if db_exercise is None:
        return False
    
    db.delete(db_exercise)
    db.commit()
    return True

# Live Session Attendance CRUD
def get_attendance_record(db: Session, id: int):
    return db.query(LiveSessionAttendance).filter(LiveSessionAttendance.id == id).first()

def get_session_attendance(db: Session, live_session_id: int):
    return db.query(LiveSessionAttendance).filter(
        LiveSessionAttendance.live_session_id == live_session_id
    ).all()

def member_check_in(db: Session, attendance: LiveSessionAttendanceCreate):
    db_attendance = LiveSessionAttendance(
        **attendance.dict(),
        check_in_time=datetime.now(),
        status=AttendanceStatus.checked_in
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def member_check_out(db: Session, id: int, attendance: LiveSessionAttendanceUpdate):
    db_attendance = get_attendance_record(db, id)
    if db_attendance is None:
        return None
    
    update_data = attendance.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_attendance, key, value)
    
    if attendance.status == AttendanceStatus.checked_out:
        db_attendance.check_out_time = datetime.now()
    
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

# Training Cycles CRUD
def get_training_cycle(db: Session, cycle_id: int):
    return db.query(TrainingCycle).filter(TrainingCycle.cycle_id == cycle_id).first()

def get_member_training_cycles(db: Session, member_id: int, active_only: bool = False):
    query = db.query(TrainingCycle).filter(TrainingCycle.member_id == member_id)
    
    if active_only:
        query = query.filter(
            TrainingCycle.status.in_([CycleStatus.planned, CycleStatus.in_progress])
        )
    
    return query.order_by(TrainingCycle.start_date.desc()).all()

def create_training_cycle(db: Session, cycle: TrainingCycleCreate):
    db_cycle = TrainingCycle(**cycle.dict(), status=CycleStatus.planned)
    db.add(db_cycle)
    db.commit()
    db.refresh(db_cycle)
    return db_cycle

def update_training_cycle(db: Session, cycle_id: int, cycle: TrainingCycleUpdate):
    db_cycle = get_training_cycle(db, cycle_id)
    if db_cycle is None:
        return None
    
    update_data = cycle.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cycle, key, value)
    
    db.commit()
    db.refresh(db_cycle)
    return db_cycle

def delete_training_cycle(db: Session, cycle_id: int):
    db_cycle = get_training_cycle(db, cycle_id)
    if db_cycle is None:
        return False
    
    db.delete(db_cycle)
    db.commit()
    return True