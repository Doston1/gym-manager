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