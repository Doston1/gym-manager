from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime, Text, Index, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..base import Base

class DifficultyLevelEnum(enum.Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Advanced = "Advanced"
    AllLevels = "All Levels"

class FocusEnum(enum.Enum):
    WeightLoss = "Weight Loss"
    MuscleGain = "Muscle Gain"
    Endurance = "Endurance"
    Flexibility = "Flexibility"
    Strength = "Strength"
    GeneralFitness = "General Fitness"

class TargetGenderEnum(enum.Enum):
    Any = "Any"
    Male = "Male"
    Female = "Female"

class MuscleGroupEnum(enum.Enum):
    Chest = "Chest"
    Back = "Back"
    Shoulders = "Shoulders"
    Arms = "Arms"
    Legs = "Legs"
    Core = "Core"
    FullBody = "Full Body"
    Cardio = "Cardio"

class RequestStatusEnum(enum.Enum):
    Pending = "Pending"
    Assigned = "Assigned"
    InProgress = "In Progress"
    Completed = "Completed"
    Cancelled = "Cancelled"

class TrainingPlan(Base):
    __tablename__ = "training_plans"
    
    plan_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    difficulty_level = Column(Enum(DifficultyLevelEnum), default=DifficultyLevelEnum.AllLevels)
    duration_weeks = Column(Integer, nullable=False)
    days_per_week = Column(Integer, nullable=False)
    primary_focus = Column(Enum(FocusEnum), nullable=False)
    secondary_focus = Column(Enum(FocusEnum))
    target_gender = Column(Enum(TargetGenderEnum), default=TargetGenderEnum.Any)
    min_age = Column(Integer)
    max_age = Column(Integer)
    equipment_needed = Column(Text)
    created_by = Column(Integer, ForeignKey("trainers.trainer_id"))
    is_custom = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    created_by_trainer = relationship("Trainer", back_populates="created_plans")
    days = relationship("TrainingPlanDay", back_populates="plan", cascade="all, delete-orphan")
    saved_by_members = relationship("MemberSavedPlan", back_populates="plan")
    custom_requests = relationship("CustomPlanRequest", back_populates="completed_plan")


class TrainingPlanDay(Base):
    __tablename__ = "training_plan_days"
    
    day_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("training_plans.plan_id", ondelete="CASCADE"), nullable=False)
    day_number = Column(Integer, nullable=False)
    name = Column(String(255))
    focus = Column(String(255))
    description = Column(Text)
    duration_minutes = Column(Integer)
    calories_burn_estimate = Column(Integer)
    
    # Relationships
    plan = relationship("TrainingPlan", back_populates="days")
    exercises = relationship("TrainingDayExercise", back_populates="day", cascade="all, delete-orphan")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('plan_id', 'day_number', name='unique_plan_day'),
    )


class Exercise(Base):
    __tablename__ = "exercises"
    
    exercise_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    difficulty_level = Column(Enum(DifficultyLevelEnum), default=DifficultyLevelEnum.Beginner)
    primary_muscle_group = Column(Enum(MuscleGroupEnum), nullable=False)
    secondary_muscle_groups = Column(Text)
    equipment_needed = Column(Text)
    image_url = Column(String(255))
    video_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    training_day_exercises = relationship("TrainingDayExercise", back_populates="exercise")


class TrainingDayExercise(Base):
    __tablename__ = "training_day_exercises"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    day_id = Column(Integer, ForeignKey("training_plan_days.day_id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.exercise_id"), nullable=False)
    order = Column(Integer, nullable=False)
    sets = Column(Integer)
    reps = Column(String(50))
    rest_seconds = Column(Integer)
    duration_seconds = Column(Integer)
    notes = Column(Text)
    
    # Relationships
    day = relationship("TrainingPlanDay", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="training_day_exercises")


class MemberSavedPlan(Base):
    __tablename__ = "member_saved_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("training_plans.plan_id"), nullable=False)
    saved_date = Column(DateTime, server_default=func.now())
    notes = Column(Text)
    
    # Relationships
    member = relationship("Member", back_populates="saved_plans")
    plan = relationship("TrainingPlan", back_populates="saved_by_members")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('member_id', 'plan_id', name='unique_member_plan'),
    )


class CustomPlanRequest(Base):
    __tablename__ = "custom_plan_requests"
    
    request_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    goal = Column(Text, nullable=False)
    days_per_week = Column(Integer, nullable=False)
    focus_areas = Column(Text)
    equipment_available = Column(Text)
    health_limitations = Column(Text)
    request_date = Column(DateTime, server_default=func.now())
    assigned_trainer_id = Column(Integer, ForeignKey("trainers.trainer_id"))
    status = Column(Enum(RequestStatusEnum), default=RequestStatusEnum.Pending)
    completed_plan_id = Column(Integer, ForeignKey("training_plans.plan_id"))
    notes = Column(Text)
    
    # Relationships
    member = relationship("Member", back_populates="custom_plan_requests")
    assigned_trainer = relationship("Trainer")
    completed_plan = relationship("TrainingPlan", back_populates="custom_requests")