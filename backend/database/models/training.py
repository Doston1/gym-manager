from sqlalchemy import TIMESTAMP, Column, Date, Integer, String, Boolean, ForeignKey, Enum, DateTime, Text, Index, Time, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, date, time
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


class TrainingPreference(Base):
    __tablename__ = "training_preferences"
    
    preference_id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    week_start_date = Column(Date, nullable=False)
    day_of_week = Column(Enum("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", name="day_of_week_enum"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    preference_type = Column(Enum("Preferred", "Available", "Not Available", name="preference_type_enum"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.trainer_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    member = relationship("Member", back_populates="training_preferences")
    trainer = relationship("Trainer")
    
    def __repr__(self):
        return f"<TrainingPreference(preference_id={self.preference_id}, member_id={self.member_id}, day={self.day_of_week}, time={self.start_time}-{self.end_time})>"

class WeeklySchedule(Base):
    __tablename__ = "weekly_schedule"
    
    schedule_id = Column(Integer, primary_key=True, index=True)
    week_start_date = Column(Date, nullable=False)
    day_of_week = Column(Enum("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", name="day_of_week_enum"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    hall_id = Column(Integer, ForeignKey("halls.hall_id", ondelete="CASCADE"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.trainer_id", ondelete="CASCADE"), nullable=False)
    max_capacity = Column(Integer, nullable=False)
    status = Column(Enum("Scheduled", "In Progress", "Completed", "Cancelled", name="schedule_status_enum"), server_default="Scheduled")
    created_by = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    hall = relationship("Hall")
    trainer = relationship("Trainer")
    creator = relationship("User", foreign_keys=[created_by])
    schedule_members = relationship("ScheduleMember", back_populates="schedule", cascade="all, delete-orphan")
    live_sessions = relationship("LiveSession", back_populates="schedule", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WeeklySchedule(schedule_id={self.schedule_id}, day={self.day_of_week}, time={self.start_time}-{self.end_time}, hall_id={self.hall_id})>"

class ScheduleMember(Base):
    __tablename__ = "schedule_members"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("weekly_schedule.schedule_id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("Assigned", "Confirmed", "Cancelled", "Attended", "No Show", name="schedule_member_status_enum"), server_default="Assigned")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    schedule = relationship("WeeklySchedule", back_populates="schedule_members")
    member = relationship("Member")
    
    def __repr__(self):
        return f"<ScheduleMember(id={self.id}, schedule_id={self.schedule_id}, member_id={self.member_id}, status={self.status})>"

class LiveSession(Base):
    __tablename__ = "live_sessions"
    
    live_session_id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("weekly_schedule.schedule_id", ondelete="CASCADE"), nullable=False)
    start_time = Column(TIMESTAMP, server_default=func.now())
    end_time = Column(TIMESTAMP, nullable=True)
    status = Column(Enum("Started", "In Progress", "Completed", "Cancelled", name="live_session_status_enum"), server_default="Started")
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    schedule = relationship("WeeklySchedule", back_populates="live_sessions")
    exercises = relationship("LiveSessionExercise", back_populates="live_session", cascade="all, delete-orphan")
    attendance = relationship("LiveSessionAttendance", back_populates="live_session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LiveSession(live_session_id={self.live_session_id}, schedule_id={self.schedule_id}, status={self.status})>"

class LiveSessionExercise(Base):
    __tablename__ = "live_session_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    live_session_id = Column(Integer, ForeignKey("live_sessions.live_session_id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.exercise_id"), nullable=False)
    sets_completed = Column(Integer, nullable=True)
    actual_reps = Column(String(100), nullable=True)
    weight_used = Column(String(100), nullable=True)
    comments = Column(Text, nullable=True)
    completed = Column(Boolean, server_default="false")
    completed_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    live_session = relationship("LiveSession", back_populates="exercises")
    member = relationship("Member")
    exercise = relationship("Exercise")
    
    def __repr__(self):
        return f"<LiveSessionExercise(id={self.id}, live_session_id={self.live_session_id}, member_id={self.member_id}, exercise_id={self.exercise_id})>"

class LiveSessionAttendance(Base):
    __tablename__ = "live_session_attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    live_session_id = Column(Integer, ForeignKey("live_sessions.live_session_id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    check_in_time = Column(TIMESTAMP, server_default=func.now())
    check_out_time = Column(TIMESTAMP, nullable=True)
    status = Column(Enum("Checked In", "Checked Out", "No Show", name="attendance_status_enum"), server_default="Checked In")
    notes = Column(Text, nullable=True)
    
    # Relationships
    live_session = relationship("LiveSession", back_populates="attendance")
    member = relationship("Member")
    
    def __repr__(self):
        return f"<LiveSessionAttendance(id={self.id}, live_session_id={self.live_session_id}, member_id={self.member_id}, status={self.status})>"

class TrainingCycle(Base):
    __tablename__ = "training_cycles"
    
    cycle_id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("training_plans.plan_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum("Planned", "In Progress", "Completed", "Cancelled", name="cycle_status_enum"), server_default="Planned")
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    member = relationship("Member")
    plan = relationship("TrainingPlan")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<TrainingCycle(cycle_id={self.cycle_id}, member_id={self.member_id}, plan_id={self.plan_id}, status={self.status})>"