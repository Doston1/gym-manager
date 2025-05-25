# backend/database/models/training.py
from sqlalchemy import (
    TIMESTAMP, Column, Date, Integer, String, Boolean, ForeignKey, 
    Enum as SqlAlchemyEnum, Text, Index, Time, UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base # Assuming Base is in backend/database/base.py

# Import all necessary Python Enums from your enums.py file
from backend.database.enums.enums import (
    DifficultyLevelEnum,
    FocusEnum,
    TargetGenderEnum,
    MuscleGroupEnum,
    RequestStatusEnum,
    TrainingDayOfWeekEnum,
    PreferenceTypeEnum,
    ScheduleStatusEnum,
    ScheduleMemberStatusEnum,
    LiveSessionStatusEnum,
    LiveAttendanceStatusEnum, # Corrected from AttendanceStatusEnum to match schema
    TrainingCycleStatusEnum   # Corrected from CycleStatus to match schema
)

class TrainingPlan(Base):
    __tablename__ = "training_plans"
    
    plan_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    difficulty_level = Column(SqlAlchemyEnum(DifficultyLevelEnum, name="tp_difficulty_level_enum"), default=DifficultyLevelEnum.AllLevels)
    duration_weeks = Column(Integer, nullable=False)
    days_per_week = Column(Integer, nullable=False)
    primary_focus = Column(SqlAlchemyEnum(FocusEnum, name="tp_primary_focus_enum"), nullable=False)
    secondary_focus = Column(SqlAlchemyEnum(FocusEnum, name="tp_secondary_focus_enum"), nullable=True)
    target_gender = Column(SqlAlchemyEnum(TargetGenderEnum, name="tp_target_gender_enum"), default=TargetGenderEnum.Any)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    equipment_needed = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("trainers.trainer_id"), nullable=True) # Can be null if system generated
    is_custom = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    created_by_trainer = relationship("Trainer", back_populates="created_plans")
    days = relationship("TrainingPlanDay", back_populates="plan", cascade="all, delete-orphan")
    saved_by_members = relationship("MemberSavedPlan", back_populates="plan")
    custom_requests = relationship("CustomPlanRequest", back_populates="completed_plan")
    # training_cycles relationship is on TrainingCycle model (back_populates="plan")


class TrainingPlanDay(Base):
    __tablename__ = "training_plan_days"
    
    day_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("training_plans.plan_id", ondelete="CASCADE"), nullable=False)
    day_number = Column(Integer, nullable=False) # 1 for day 1, 2 for day 2, etc.
    name = Column(String(255), nullable=True)
    focus = Column(String(255), nullable=True) # E.g., "Chest and Triceps", "Lower Body", etc.
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    calories_burn_estimate = Column(Integer, nullable=True)
    
    # Relationships
    plan = relationship("TrainingPlan", back_populates="days")
    exercises = relationship("TrainingDayExercise", back_populates="day", cascade="all, delete-orphan")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('plan_id', 'day_number', name='uq_plan_day_number'),
    )


class Exercise(Base):
    __tablename__ = "exercises"
    
    exercise_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True) # Exercise names should ideally be unique
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    difficulty_level = Column(SqlAlchemyEnum(DifficultyLevelEnum, name="ex_difficulty_level_enum"), default=DifficultyLevelEnum.Beginner)
    primary_muscle_group = Column(SqlAlchemyEnum(MuscleGroupEnum, name="ex_muscle_group_enum"), nullable=False)
    secondary_muscle_groups = Column(Text, nullable=True) # Could be comma-separated string or JSON
    equipment_needed = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    video_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    training_day_exercises = relationship("TrainingDayExercise", back_populates="exercise")
    live_session_exercises = relationship("LiveSessionExercise", back_populates="exercise") # Added


class TrainingDayExercise(Base):
    __tablename__ = "training_day_exercises"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    day_id = Column(Integer, ForeignKey("training_plan_days.day_id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.exercise_id"), nullable=False)
    order = Column(Integer, nullable=False) # Sequence of exercises within the day
    sets = Column(Integer, nullable=True)
    reps = Column(String(50), nullable=True) # Could be a range like "8-12" or specific like "10"
    rest_seconds = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True) # For timed exercises
    notes = Column(Text, nullable=True)
    
    # Relationships
    day = relationship("TrainingPlanDay", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="training_day_exercises")


class MemberSavedPlan(Base):
    __tablename__ = "member_saved_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("training_plans.plan_id"), nullable=False)
    saved_date = Column(TIMESTAMP, server_default=func.now())
    notes = Column(Text, nullable=True)
    
    # Relationships
    member = relationship("Member", back_populates="saved_plans")
    plan = relationship("TrainingPlan", back_populates="saved_by_members")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('member_id', 'plan_id', name='uq_member_plan_save'),
    )


class CustomPlanRequest(Base):
    __tablename__ = "custom_plan_requests"
    
    request_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    goal = Column(Text, nullable=False)
    days_per_week = Column(Integer, nullable=False)
    focus_areas = Column(Text, nullable=True)
    equipment_available = Column(Text, nullable=True)
    health_limitations = Column(Text, nullable=True)
    request_date = Column(TIMESTAMP, server_default=func.now())
    assigned_trainer_id = Column(Integer, ForeignKey("trainers.trainer_id"), nullable=True)
    status = Column(SqlAlchemyEnum(RequestStatusEnum, name="cpr_status_enum"), default=RequestStatusEnum.Pending)
    completed_plan_id = Column(Integer, ForeignKey("training_plans.plan_id"), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    member = relationship("Member", back_populates="custom_plan_requests")
    assigned_trainer = relationship("Trainer") # No back_populates needed if Trainer doesn't need to see requests directly
    completed_plan = relationship("TrainingPlan", back_populates="custom_requests")


class TrainingPreference(Base):
    __tablename__ = "training_preferences"
    
    preference_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    week_start_date = Column(Date, nullable=False)
    day_of_week = Column(SqlAlchemyEnum(TrainingDayOfWeekEnum, name="tp_model_day_of_week_enum"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    preference_type = Column(SqlAlchemyEnum(PreferenceTypeEnum, name="tp_model_preference_type_enum"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.trainer_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    member = relationship("Member", back_populates="training_preferences")
    trainer = relationship("Trainer") # No back_populates needed if Trainer doesn't see preferences directly
    
    __table_args__ = (
        UniqueConstraint('member_id', 'week_start_date', 'day_of_week', 'start_time', 'end_time', name='uq_member_preference_slot'),
        Index('idx_tp_week_member', 'week_start_date', 'member_id'),
    )
    
    def __repr__(self):
        return f"<TrainingPreference(id={self.preference_id}, member={self.member_id}, day={self.day_of_week.value})>"


class WeeklySchedule(Base):
    __tablename__ = "weekly_schedule"
    
    schedule_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    week_start_date = Column(Date, nullable=False, index=True)
    day_of_week = Column(SqlAlchemyEnum(TrainingDayOfWeekEnum, name="ws_model_day_of_week_enum"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    hall_id = Column(Integer, ForeignKey("halls.hall_id", ondelete="CASCADE"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.trainer_id", ondelete="CASCADE"), nullable=False)
    max_capacity = Column(Integer, nullable=False)
    status = Column(SqlAlchemyEnum(ScheduleStatusEnum, name="ws_model_status_enum"), default=ScheduleStatusEnum.scheduled)
    created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True) # Allow null if system creates
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    hall = relationship("Hall") # Assumes Hall model has back_populates="weekly_schedules" or similar
    trainer = relationship("Trainer") # Assumes Trainer model has back_populates="weekly_schedules"
    creator = relationship("User") # No back_populates needed if User doesn't track created schedules
    schedule_members = relationship("ScheduleMember", back_populates="schedule", cascade="all, delete-orphan")
    live_sessions = relationship("LiveSession", back_populates="schedule", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_ws_week_day_time_hall_trainer', 'week_start_date', 'day_of_week', 'start_time', 'hall_id', 'trainer_id', unique=True),
    )

    def __repr__(self):
        return f"<WeeklySchedule(id={self.schedule_id}, day={self.day_of_week.value}, time={self.start_time})>"


class ScheduleMember(Base):
    __tablename__ = "schedule_members"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("weekly_schedule.schedule_id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    status = Column(SqlAlchemyEnum(ScheduleMemberStatusEnum, name="sm_model_status_enum"), default=ScheduleMemberStatusEnum.assigned)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    schedule = relationship("WeeklySchedule", back_populates="schedule_members")
    member = relationship("Member") # Assumes Member model has back_populates="scheduled_sessions" or similar
    
    __table_args__ = (
        UniqueConstraint('schedule_id', 'member_id', name='uq_schedule_member_assignment'),
        Index('idx_sm_member_schedule', 'member_id', 'schedule_id'),
    )
    
    def __repr__(self):
        return f"<ScheduleMember(id={self.id}, schedule={self.schedule_id}, member={self.member_id})>"


class LiveSession(Base):
    __tablename__ = "live_sessions"
    
    live_session_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("weekly_schedule.schedule_id", ondelete="CASCADE"), nullable=False, unique=True) # One live session per schedule entry
    start_time = Column(TIMESTAMP, server_default=func.now())
    end_time = Column(TIMESTAMP, nullable=True)
    status = Column(SqlAlchemyEnum(LiveSessionStatusEnum, name="ls_model_status_enum"), default=LiveSessionStatusEnum.started)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    schedule = relationship("WeeklySchedule", back_populates="live_sessions", uselist=False) # One-to-one with WeeklySchedule
    exercises = relationship("LiveSessionExercise", back_populates="live_session", cascade="all, delete-orphan")
    attendance = relationship("LiveSessionAttendance", back_populates="live_session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LiveSession(id={self.live_session_id}, schedule={self.schedule_id}, status={self.status.value})>"


class LiveSessionExercise(Base):
    __tablename__ = "live_session_exercises"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    live_session_id = Column(Integer, ForeignKey("live_sessions.live_session_id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.exercise_id"), nullable=False) # From Exercise table
    # planned_sets = Column(Integer, nullable=True) # Could be copied from TrainingPlanDayExercise
    # planned_reps = Column(String(100), nullable=True)
    sets_completed = Column(Integer, nullable=True)
    actual_reps = Column(String(100), nullable=True) # e.g., "10,8,8"
    weight_used = Column(String(100), nullable=True) # e.g., "50kg,45kg,40kg" or "BW"
    comments = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    live_session = relationship("LiveSession", back_populates="exercises")
    member = relationship("Member") # Assumes Member has back_populates="live_exercises"
    exercise = relationship("Exercise", back_populates="live_session_exercises") # Assumes Exercise has back_populates
    
    __table_args__ = (
        UniqueConstraint('live_session_id', 'member_id', 'exercise_id', name='uq_live_session_member_exercise'),
        Index('idx_lse_session_member', 'live_session_id', 'member_id'),
    )

    def __repr__(self):
        return f"<LiveSessionExercise(id={self.id}, member={self.member_id}, ex={self.exercise_id})>"


class LiveSessionAttendance(Base):
    __tablename__ = "live_session_attendance"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    live_session_id = Column(Integer, ForeignKey("live_sessions.live_session_id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    check_in_time = Column(TIMESTAMP, server_default=func.now())
    check_out_time = Column(TIMESTAMP, nullable=True)
    status = Column(SqlAlchemyEnum(LiveAttendanceStatusEnum, name="lsa_model_status_enum"), default=LiveAttendanceStatusEnum.checked_in)
    notes = Column(Text, nullable=True)
    
    # Relationships
    live_session = relationship("LiveSession", back_populates="attendance")
    member = relationship("Member") # Assumes Member has back_populates="live_attendance"
    
    __table_args__ = (
        UniqueConstraint('live_session_id', 'member_id', name='uq_live_session_attendance'),
    )

    def __repr__(self):
        return f"<LiveSessionAttendance(id={self.id}, member={self.member_id}, status={self.status.value})>"


class TrainingCycle(Base): # Represents a member's enrollment in a specific training plan for a period
    __tablename__ = "training_cycles"
    
    cycle_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("training_plans.plan_id"), nullable=False) # The base plan
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False) # Calculated: start_date + plan.duration_weeks
    status = Column(SqlAlchemyEnum(TrainingCycleStatusEnum, name="tc_model_status_enum"), default=TrainingCycleStatusEnum.planned)
    created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True) # Who assigned this cycle
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    member = relationship("Member") # Assumes Member has back_populates="training_cycles"
    plan = relationship("TrainingPlan") # Assumes TrainingPlan has back_populates="active_cycles" or similar
    creator = relationship("User") # No back_populates usually needed here

    def __repr__(self):
        return f"<TrainingCycle(id={self.cycle_id}, member={self.member_id}, plan={self.plan_id})>"
    




# --------------------------------------
# from sqlalchemy import TIMESTAMP, Column, Date, Integer, String, Boolean, ForeignKey, Enum, DateTime, Text, Index, Time, UniqueConstraint
# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship
# from datetime import datetime, date, time
# import enum
# from ..base import Base

# class DifficultyLevelEnum(enum.Enum):
#     Beginner = "Beginner"
#     Intermediate = "Intermediate"
#     Advanced = "Advanced"
#     AllLevels = "All Levels"

# class FocusEnum(enum.Enum):
#     WeightLoss = "Weight Loss"
#     MuscleGain = "Muscle Gain"
#     Endurance = "Endurance"
#     Flexibility = "Flexibility"
#     Strength = "Strength"
#     GeneralFitness = "General Fitness"

# class TargetGenderEnum(enum.Enum):
#     Any = "Any"
#     Male = "Male"
#     Female = "Female"

# class MuscleGroupEnum(enum.Enum):
#     Chest = "Chest"
#     Back = "Back"
#     Shoulders = "Shoulders"
#     Arms = "Arms"
#     Legs = "Legs"
#     Core = "Core"
#     FullBody = "Full Body"
#     Cardio = "Cardio"

# class RequestStatusEnum(enum.Enum):
#     Pending = "Pending"
#     Assigned = "Assigned"
#     InProgress = "In Progress"
#     Completed = "Completed"
#     Cancelled = "Cancelled"

# class TrainingPlan(Base):
#     __tablename__ = "training_plans"
    
#     plan_id = Column(Integer, primary_key=True, autoincrement=True)
#     title = Column(String(255), nullable=False)
#     description = Column(Text)
#     difficulty_level = Column(Enum(DifficultyLevelEnum), default=DifficultyLevelEnum.AllLevels)
#     duration_weeks = Column(Integer, nullable=False)
#     days_per_week = Column(Integer, nullable=False)
#     primary_focus = Column(Enum(FocusEnum), nullable=False)
#     secondary_focus = Column(Enum(FocusEnum))
#     target_gender = Column(Enum(TargetGenderEnum), default=TargetGenderEnum.Any)
#     min_age = Column(Integer)
#     max_age = Column(Integer)
#     equipment_needed = Column(Text)
#     created_by = Column(Integer, ForeignKey("trainers.trainer_id"))
#     is_custom = Column(Boolean, default=False)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
#     # Relationships
#     created_by_trainer = relationship("Trainer", back_populates="created_plans")
#     days = relationship("TrainingPlanDay", back_populates="plan", cascade="all, delete-orphan")
#     saved_by_members = relationship("MemberSavedPlan", back_populates="plan")
#     custom_requests = relationship("CustomPlanRequest", back_populates="completed_plan")


# class TrainingPlanDay(Base):
#     __tablename__ = "training_plan_days"
    
#     day_id = Column(Integer, primary_key=True, autoincrement=True)
#     plan_id = Column(Integer, ForeignKey("training_plans.plan_id", ondelete="CASCADE"), nullable=False)
#     day_number = Column(Integer, nullable=False)
#     name = Column(String(255))
#     focus = Column(String(255))
#     description = Column(Text)
#     duration_minutes = Column(Integer)
#     calories_burn_estimate = Column(Integer)
    
#     # Relationships
#     plan = relationship("TrainingPlan", back_populates="days")
#     exercises = relationship("TrainingDayExercise", back_populates="day", cascade="all, delete-orphan")
    
#     # Unique constraint
#     __table_args__ = (
#         UniqueConstraint('plan_id', 'day_number', name='unique_plan_day'),
#     )


# class Exercise(Base):
#     __tablename__ = "exercises"
    
#     exercise_id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String(255), nullable=False)
#     description = Column(Text)
#     instructions = Column(Text)
#     difficulty_level = Column(Enum(DifficultyLevelEnum), default=DifficultyLevelEnum.Beginner)
#     primary_muscle_group = Column(Enum(MuscleGroupEnum), nullable=False)
#     secondary_muscle_groups = Column(Text)
#     equipment_needed = Column(Text)
#     image_url = Column(String(255))
#     video_url = Column(String(255))
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
#     # Relationships
#     training_day_exercises = relationship("TrainingDayExercise", back_populates="exercise")


# class TrainingDayExercise(Base):
#     __tablename__ = "training_day_exercises"
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     day_id = Column(Integer, ForeignKey("training_plan_days.day_id", ondelete="CASCADE"), nullable=False)
#     exercise_id = Column(Integer, ForeignKey("exercises.exercise_id"), nullable=False)
#     order = Column(Integer, nullable=False)
#     sets = Column(Integer)
#     reps = Column(String(50))
#     rest_seconds = Column(Integer)
#     duration_seconds = Column(Integer)
#     notes = Column(Text)
    
#     # Relationships
#     day = relationship("TrainingPlanDay", back_populates="exercises")
#     exercise = relationship("Exercise", back_populates="training_day_exercises")


# class MemberSavedPlan(Base):
#     __tablename__ = "member_saved_plans"
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
#     plan_id = Column(Integer, ForeignKey("training_plans.plan_id"), nullable=False)
#     saved_date = Column(DateTime, server_default=func.now())
#     notes = Column(Text)
    
#     # Relationships
#     member = relationship("Member", back_populates="saved_plans")
#     plan = relationship("TrainingPlan", back_populates="saved_by_members")
    
#     # Unique constraint
#     __table_args__ = (
#         UniqueConstraint('member_id', 'plan_id', name='unique_member_plan'),
#     )


# class CustomPlanRequest(Base):
#     __tablename__ = "custom_plan_requests"
    
#     request_id = Column(Integer, primary_key=True, autoincrement=True)
#     member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
#     goal = Column(Text, nullable=False)
#     days_per_week = Column(Integer, nullable=False)
#     focus_areas = Column(Text)
#     equipment_available = Column(Text)
#     health_limitations = Column(Text)
#     request_date = Column(DateTime, server_default=func.now())
#     assigned_trainer_id = Column(Integer, ForeignKey("trainers.trainer_id"))
#     status = Column(Enum(RequestStatusEnum), default=RequestStatusEnum.Pending)
#     completed_plan_id = Column(Integer, ForeignKey("training_plans.plan_id"))
#     notes = Column(Text)
    
#     # Relationships
#     member = relationship("Member", back_populates="custom_plan_requests")
#     assigned_trainer = relationship("Trainer")
#     completed_plan = relationship("TrainingPlan", back_populates="custom_requests")


# class TrainingPreference(Base):
#     __tablename__ = "training_preferences"
    
#     preference_id = Column(Integer, primary_key=True, index=True)
#     member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
#     week_start_date = Column(Date, nullable=False)
#     day_of_week = Column(Enum("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", name="day_of_week_enum"), nullable=False)
#     start_time = Column(Time, nullable=False)
#     end_time = Column(Time, nullable=False)
#     preference_type = Column(Enum("Preferred", "Available", "Not Available", name="preference_type_enum"), nullable=False)
#     trainer_id = Column(Integer, ForeignKey("trainers.trainer_id", ondelete="SET NULL"), nullable=True)
#     created_at = Column(TIMESTAMP, server_default=func.now())
    
#     # Relationships
#     member = relationship("Member", back_populates="training_preferences")
#     trainer = relationship("Trainer")
    
#     def __repr__(self):
#         return f"<TrainingPreference(preference_id={self.preference_id}, member_id={self.member_id}, day={self.day_of_week}, time={self.start_time}-{self.end_time})>"

# class WeeklySchedule(Base):
#     __tablename__ = "weekly_schedule"
    
#     schedule_id = Column(Integer, primary_key=True, index=True)
#     week_start_date = Column(Date, nullable=False)
#     day_of_week = Column(Enum("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", name="day_of_week_enum"), nullable=False)
#     start_time = Column(Time, nullable=False)
#     end_time = Column(Time, nullable=False)
#     hall_id = Column(Integer, ForeignKey("halls.hall_id", ondelete="CASCADE"), nullable=False)
#     trainer_id = Column(Integer, ForeignKey("trainers.trainer_id", ondelete="CASCADE"), nullable=False)
#     max_capacity = Column(Integer, nullable=False)
#     status = Column(Enum("Scheduled", "In Progress", "Completed", "Cancelled", name="schedule_status_enum"), server_default="Scheduled")
#     created_by = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
#     created_at = Column(TIMESTAMP, server_default=func.now())
#     updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
#     # Relationships
#     hall = relationship("Hall")
#     trainer = relationship("Trainer")
#     creator = relationship("User", foreign_keys=[created_by])
#     schedule_members = relationship("ScheduleMember", back_populates="schedule", cascade="all, delete-orphan")
#     live_sessions = relationship("LiveSession", back_populates="schedule", cascade="all, delete-orphan")
    
#     def __repr__(self):
#         return f"<WeeklySchedule(schedule_id={self.schedule_id}, day={self.day_of_week}, time={self.start_time}-{self.end_time}, hall_id={self.hall_id})>"

# class ScheduleMember(Base):
#     __tablename__ = "schedule_members"
    
#     id = Column(Integer, primary_key=True, index=True)
#     schedule_id = Column(Integer, ForeignKey("weekly_schedule.schedule_id", ondelete="CASCADE"), nullable=False)
#     member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
#     status = Column(Enum("Assigned", "Confirmed", "Cancelled", "Attended", "No Show", name="schedule_member_status_enum"), server_default="Assigned")
#     created_at = Column(TIMESTAMP, server_default=func.now())
#     updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
#     # Relationships
#     schedule = relationship("WeeklySchedule", back_populates="schedule_members")
#     member = relationship("Member")
    
#     def __repr__(self):
#         return f"<ScheduleMember(id={self.id}, schedule_id={self.schedule_id}, member_id={self.member_id}, status={self.status})>"

# class LiveSession(Base):
#     __tablename__ = "live_sessions"
    
#     live_session_id = Column(Integer, primary_key=True, index=True)
#     schedule_id = Column(Integer, ForeignKey("weekly_schedule.schedule_id", ondelete="CASCADE"), nullable=False)
#     start_time = Column(TIMESTAMP, server_default=func.now())
#     end_time = Column(TIMESTAMP, nullable=True)
#     status = Column(Enum("Started", "In Progress", "Completed", "Cancelled", name="live_session_status_enum"), server_default="Started")
#     notes = Column(Text)
#     created_at = Column(TIMESTAMP, server_default=func.now())
#     updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
#     # Relationships
#     schedule = relationship("WeeklySchedule", back_populates="live_sessions")
#     exercises = relationship("LiveSessionExercise", back_populates="live_session", cascade="all, delete-orphan")
#     attendance = relationship("LiveSessionAttendance", back_populates="live_session", cascade="all, delete-orphan")
    
#     def __repr__(self):
#         return f"<LiveSession(live_session_id={self.live_session_id}, schedule_id={self.schedule_id}, status={self.status})>"

# class LiveSessionExercise(Base):
#     __tablename__ = "live_session_exercises"
    
#     id = Column(Integer, primary_key=True, index=True)
#     live_session_id = Column(Integer, ForeignKey("live_sessions.live_session_id", ondelete="CASCADE"), nullable=False)
#     member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
#     exercise_id = Column(Integer, ForeignKey("exercises.exercise_id"), nullable=False)
#     sets_completed = Column(Integer, nullable=True)
#     actual_reps = Column(String(100), nullable=True)
#     weight_used = Column(String(100), nullable=True)
#     comments = Column(Text, nullable=True)
#     completed = Column(Boolean, server_default="false")
#     completed_at = Column(TIMESTAMP, nullable=True)
#     created_at = Column(TIMESTAMP, server_default=func.now())
#     updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
#     # Relationships
#     live_session = relationship("LiveSession", back_populates="exercises")
#     member = relationship("Member")
#     exercise = relationship("Exercise")
    
#     def __repr__(self):
#         return f"<LiveSessionExercise(id={self.id}, live_session_id={self.live_session_id}, member_id={self.member_id}, exercise_id={self.exercise_id})>"

# class LiveSessionAttendance(Base):
#     __tablename__ = "live_session_attendance"
    
#     id = Column(Integer, primary_key=True, index=True)
#     live_session_id = Column(Integer, ForeignKey("live_sessions.live_session_id", ondelete="CASCADE"), nullable=False)
#     member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
#     check_in_time = Column(TIMESTAMP, server_default=func.now())
#     check_out_time = Column(TIMESTAMP, nullable=True)
#     status = Column(Enum("Checked In", "Checked Out", "No Show", name="attendance_status_enum"), server_default="Checked In")
#     notes = Column(Text, nullable=True)
    
#     # Relationships
#     live_session = relationship("LiveSession", back_populates="attendance")
#     member = relationship("Member")
    
#     def __repr__(self):
#         return f"<LiveSessionAttendance(id={self.id}, live_session_id={self.live_session_id}, member_id={self.member_id}, status={self.status})>"

# class TrainingCycle(Base):
#     __tablename__ = "training_cycles"
    
#     cycle_id = Column(Integer, primary_key=True, index=True)
#     member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
#     plan_id = Column(Integer, ForeignKey("training_plans.plan_id"), nullable=False)
#     start_date = Column(Date, nullable=False)
#     end_date = Column(Date, nullable=False)
#     status = Column(Enum("Planned", "In Progress", "Completed", "Cancelled", name="cycle_status_enum"), server_default="Planned")
#     created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
#     created_at = Column(TIMESTAMP, server_default=func.now())
#     updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
#     # Relationships
#     member = relationship("Member")
#     plan = relationship("TrainingPlan")
#     creator = relationship("User", foreign_keys=[created_by])
    
#     def __repr__(self):
#         return f"<TrainingCycle(cycle_id={self.cycle_id}, member_id={self.member_id}, plan_id={self.plan_id}, status={self.status})>"