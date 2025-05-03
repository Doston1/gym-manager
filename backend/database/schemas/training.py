from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from backend.database.models.training import (
    DifficultyLevelEnum,
    FocusEnum,
    TargetGenderEnum,
    MuscleGroupEnum,
    RequestStatusEnum,
)


# ✅ TrainingPlan Schemas
class TrainingPlanBase(BaseModel):
    title: str
    description: Optional[str]
    difficulty_level: DifficultyLevelEnum = DifficultyLevelEnum.AllLevels
    duration_weeks: int
    days_per_week: int
    primary_focus: FocusEnum
    secondary_focus: Optional[FocusEnum]
    target_gender: TargetGenderEnum = TargetGenderEnum.Any
    min_age: Optional[int]
    max_age: Optional[int]
    equipment_needed: Optional[str]
    is_custom: bool = False
    is_active: bool = True


class TrainingPlanCreate(TrainingPlanBase):
    created_by: Optional[int]  # Trainer ID

class TrainingPlanUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    difficulty_level: Optional[DifficultyLevelEnum]
    duration_weeks: Optional[int]
    days_per_week: Optional[int]
    primary_focus: Optional[FocusEnum]
    secondary_focus: Optional[FocusEnum]
    target_gender: Optional[TargetGenderEnum]
    min_age: Optional[int]
    max_age: Optional[int]
    equipment_needed: Optional[str]
    is_custom: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True


class TrainingPlanResponse(TrainingPlanBase):
    plan_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ✅ TrainingPlanDay Schemas
class TrainingPlanDayBase(BaseModel):
    plan_id: int
    day_number: int
    name: Optional[str]
    focus: Optional[str]
    description: Optional[str]
    duration_minutes: Optional[int]
    calories_burn_estimate: Optional[int]


class TrainingPlanDayCreate(TrainingPlanDayBase):
    pass


class TrainingPlanDayResponse(TrainingPlanDayBase):
    day_id: int

    class Config:
        orm_mode = True


# ✅ Exercise Schemas
class ExerciseBase(BaseModel):
    name: str
    description: Optional[str]
    instructions: Optional[str]
    difficulty_level: DifficultyLevelEnum = DifficultyLevelEnum.Beginner
    primary_muscle_group: MuscleGroupEnum
    secondary_muscle_groups: Optional[str]
    equipment_needed: Optional[str]
    image_url: Optional[str]
    video_url: Optional[str]
    is_active: bool = True


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseResponse(ExerciseBase):
    exercise_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ✅ TrainingDayExercise Schemas
class TrainingDayExerciseBase(BaseModel):
    day_id: int
    exercise_id: int
    order: int
    sets: Optional[int]
    reps: Optional[str]
    rest_seconds: Optional[int]
    duration_seconds: Optional[int]
    notes: Optional[str]


class TrainingDayExerciseCreate(TrainingDayExerciseBase):
    pass


class TrainingDayExerciseResponse(TrainingDayExerciseBase):
    id: int

    class Config:
        orm_mode = True


# ✅ MemberSavedPlan Schemas
class MemberSavedPlanBase(BaseModel):
    member_id: int
    plan_id: int
    notes: Optional[str]


class MemberSavedPlanCreate(MemberSavedPlanBase):
    pass


class MemberSavedPlanResponse(MemberSavedPlanBase):
    id: int
    saved_date: datetime

    class Config:
        orm_mode = True


# ✅ CustomPlanRequest Schemas
class CustomPlanRequestBase(BaseModel):
    member_id: int
    goal: str
    days_per_week: int
    focus_areas: Optional[str]
    equipment_available: Optional[str]
    health_limitations: Optional[str]
    assigned_trainer_id: Optional[int]
    status: RequestStatusEnum = RequestStatusEnum.Pending
    notes: Optional[str]


class CustomPlanRequestCreate(CustomPlanRequestBase):
    pass


class CustomPlanRequestResponse(CustomPlanRequestBase):
    request_id: int
    request_date: datetime
    completed_plan_id: Optional[int]

    class Config:
        orm_mode = True


from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

# Training Preferences Schemas

class TrainingPreferenceBase(BaseModel):
    day_of_week: str
    start_time: str
    end_time: str
    preference_type: str
    trainer_id: Optional[int] = None

class TrainingPreferenceCreate(TrainingPreferenceBase):
    member_id: int
    week_start_date: datetime.date

class TrainingPreferenceUpdate(BaseModel):
    preference_type: str
    trainer_id: Optional[int] = None

class TrainingPreferenceResponse(TrainingPreferenceBase):
    preference_id: int
    member_id: int
    week_start_date: datetime.date
    created_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

# Weekly Schedule Schemas

class WeeklyScheduleBase(BaseModel):
    hall_id: int
    trainer_id: int
    day_of_week: str
    start_time: str
    end_time: str
    week_start_date: datetime.date
    max_capacity: int

class WeeklyScheduleCreate(WeeklyScheduleBase):
    pass

class WeeklyScheduleResponse(WeeklyScheduleBase):
    schedule_id: int
    current_capacity: int
    status: str
    hall_name: Optional[str] = None
    trainer_name: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

class MemberScheduleAssignmentCreate(BaseModel):
    schedule_id: int
    member_id: int

class MemberScheduleAssignmentResponse(BaseModel):
    assignment_id: int
    schedule_id: int
    member_id: int
    attendance_status: str
    check_in_time: Optional[datetime.datetime] = None
    check_out_time: Optional[datetime.datetime] = None
    notes: Optional[str] = None
    created_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

# Training Cycle Schemas

class TrainingCycleBase(BaseModel):
    name: str
    description: Optional[str] = None

class TrainingCycleCreate(TrainingCycleBase):
    pass

class TrainingCycleResponse(TrainingCycleBase):
    cycle_id: int
    is_active: bool
    created_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

class TrainingCycleSessionBase(BaseModel):
    cycle_id: int
    session_number: int
    muscle_focus: str
    duration_minutes: int = 90
    description: Optional[str] = None

class TrainingCycleSessionCreate(TrainingCycleSessionBase):
    pass

class TrainingCycleSessionResponse(TrainingCycleSessionBase):
    session_id: int
    exercises: Optional[List] = None

    class Config:
        orm_mode = True

class SessionExerciseBase(BaseModel):
    session_id: int
    exercise_id: int
    order: int
    sets: int
    reps: str
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None

class SessionExerciseCreate(SessionExerciseBase):
    pass

class SessionExerciseResponse(SessionExerciseBase):
    id: int
    exercise_name: Optional[str] = None
    primary_muscle_group: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        orm_mode = True

# Live Training Session Schemas

class LiveTrainingSessionBase(BaseModel):
    schedule_id: int

class LiveTrainingSessionCreate(LiveTrainingSessionBase):
    pass

class LiveTrainingSessionResponse(LiveTrainingSessionBase):
    live_session_id: int
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    status: str
    notes: Optional[str] = None
    # Additional fields from join
    day_of_week: Optional[str] = None
    hall_name: Optional[str] = None
    trainer_name: Optional[str] = None

    class Config:
        orm_mode = True

class MemberProgressBase(BaseModel):
    live_session_id: int
    member_id: int
    exercise_id: int
    sets_completed: int = 0
    actual_reps: Optional[str] = None
    weight_used: Optional[str] = None
    comments: Optional[str] = None

class MemberProgressUpdate(BaseModel):
    sets_completed: int
    actual_reps: str
    weight_used: str
    comments: Optional[str] = None

class MemberProgressResponse(MemberProgressBase):
    progress_id: int
    completed: bool
    exercise_name: Optional[str] = None
    primary_muscle_group: Optional[str] = None
    instructions: Optional[str] = None

    class Config:
        orm_mode = True

# Week preference selection request/response
class WeekPreferenceRequest(BaseModel):
    week_start_date: Optional[datetime.date] = None

class WeekPreferenceResponse(BaseModel):
    can_set_preferences: bool
    week_start_date: datetime.date
    preferences: List[TrainingPreferenceResponse] = []

# Member active plan schemas
class MemberActivePlanBase(BaseModel):
    member_id: int
    plan_id: int
    start_date: datetime.date
    end_date: Optional[datetime.date] = None

class MemberActivePlanCreate(MemberActivePlanBase):
    pass

class MemberActivePlanResponse(MemberActivePlanBase):
    active_plan_id: int
    status: str
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True


from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime, date, time
from enum import Enum

# Enums
class PreferenceType(str, Enum):
    preferred = "Preferred"
    available = "Available"
    not_available = "Not Available"

class DayOfWeek(str, Enum):
    sunday = "Sunday"
    monday = "Monday"
    tuesday = "Tuesday"
    wednesday = "Wednesday"
    thursday = "Thursday"
    
class ScheduleStatus(str, Enum):
    scheduled = "Scheduled"
    in_progress = "In Progress"
    completed = "Completed"
    cancelled = "Cancelled"
    
class ScheduleMemberStatus(str, Enum):
    assigned = "Assigned"
    confirmed = "Confirmed"
    cancelled = "Cancelled"
    attended = "Attended"
    no_show = "No Show"
    
class LiveSessionStatus(str, Enum):
    started = "Started"
    in_progress = "In Progress"
    completed = "Completed"
    cancelled = "Cancelled"
    
class AttendanceStatus(str, Enum):
    checked_in = "Checked In"
    checked_out = "Checked Out"
    no_show = "No Show"
    
class CycleStatus(str, Enum):
    planned = "Planned"
    in_progress = "In Progress"
    completed = "Completed"
    cancelled = "Cancelled"

# Base schemas
class TrainingPreferenceBase(BaseModel):
    week_start_date: date
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    preference_type: PreferenceType
    trainer_id: Optional[int] = None
    
class WeeklyScheduleBase(BaseModel):
    week_start_date: date
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    hall_id: int
    trainer_id: int
    max_capacity: int
    
class ScheduleMemberBase(BaseModel):
    member_id: int
    status: ScheduleMemberStatus = ScheduleMemberStatus.assigned
    
class LiveSessionBase(BaseModel):
    schedule_id: int
    notes: Optional[str] = None
    
class LiveSessionExerciseBase(BaseModel):
    member_id: int
    exercise_id: int
    sets_completed: Optional[int] = None
    actual_reps: Optional[str] = None
    weight_used: Optional[str] = None
    comments: Optional[str] = None
    
class LiveSessionAttendanceBase(BaseModel):
    member_id: int
    notes: Optional[str] = None
    
class TrainingCycleBase(BaseModel):
    member_id: int
    plan_id: int
    start_date: date
    end_date: date

# Create schemas - for accepting data when creating new records
class TrainingPreferenceCreate(TrainingPreferenceBase):
    member_id: int
    
class WeeklyScheduleCreate(WeeklyScheduleBase):
    created_by: int
    
class ScheduleMemberCreate(ScheduleMemberBase):
    schedule_id: int
    
class LiveSessionCreate(LiveSessionBase):
    pass
    
class LiveSessionExerciseCreate(LiveSessionExerciseBase):
    live_session_id: int
    
class LiveSessionAttendanceCreate(LiveSessionAttendanceBase):
    live_session_id: int
    
class TrainingCycleCreate(TrainingCycleBase):
    created_by: int

# Update schemas - for accepting data when updating records
class TrainingPreferenceUpdate(BaseModel):
    preference_type: Optional[PreferenceType] = None
    trainer_id: Optional[int] = None
    
class WeeklyScheduleUpdate(BaseModel):
    hall_id: Optional[int] = None
    trainer_id: Optional[int] = None
    max_capacity: Optional[int] = None
    status: Optional[ScheduleStatus] = None
    
class ScheduleMemberUpdate(BaseModel):
    status: Optional[ScheduleMemberStatus] = None
    
class LiveSessionUpdate(BaseModel):
    status: Optional[LiveSessionStatus] = None
    notes: Optional[str] = None
    end_time: Optional[datetime] = None
    
class LiveSessionExerciseUpdate(BaseModel):
    sets_completed: Optional[int] = None
    actual_reps: Optional[str] = None
    weight_used: Optional[str] = None
    comments: Optional[str] = None
    completed: Optional[bool] = None
    
class LiveSessionAttendanceUpdate(BaseModel):
    check_out_time: Optional[datetime] = None
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None
    
class TrainingCycleUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[CycleStatus] = None

# Response schemas - for returning data
class TrainingPreference(TrainingPreferenceBase):
    preference_id: int
    member_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        
class ScheduleMember(ScheduleMemberBase):
    id: int
    schedule_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        
class WeeklySchedule(WeeklyScheduleBase):
    schedule_id: int
    status: ScheduleStatus
    created_by: int
    created_at: datetime
    updated_at: datetime
    schedule_members: List[ScheduleMember] = []
    
    class Config:
        orm_mode = True
        
class LiveSessionAttendance(LiveSessionAttendanceBase):
    id: int
    live_session_id: int
    check_in_time: datetime
    check_out_time: Optional[datetime] = None
    status: AttendanceStatus
    
    class Config:
        orm_mode = True
        
class LiveSessionExercise(LiveSessionExerciseBase):
    id: int
    live_session_id: int
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        
class LiveSession(LiveSessionBase):
    live_session_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    status: LiveSessionStatus
    created_at: datetime
    updated_at: datetime
    exercises: List[LiveSessionExercise] = []
    attendance: List[LiveSessionAttendance] = []
    
    class Config:
        orm_mode = True
        
class TrainingCycle(TrainingCycleBase):
    cycle_id: int
    status: CycleStatus
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Enhanced response schemas with additional related data
class WeeklyScheduleWithDetails(WeeklySchedule):
    hall_name: str
    trainer_name: str
    
    class Config:
        orm_mode = True
        
class LiveSessionWithDetails(LiveSession):
    schedule_day: DayOfWeek
    schedule_start_time: time
    schedule_end_time: time
    hall_name: str
    trainer_name: str
    
    class Config:
        orm_mode = True