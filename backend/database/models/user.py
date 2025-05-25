# backend/database/models/user.py
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Enum, DateTime, Text, Float # Added Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..base import Base

class GenderEnum(enum.Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"
    PreferNotToSay = "Prefer not to say"

class UserTypeEnum(enum.Enum):
    member = "member"
    trainer = "trainer"
    manager = "manager"

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    firebase_uid = Column(String(128), unique=True, nullable=False) # Made nullable=False
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True) # Explicitly nullable
    date_of_birth = Column(Date, nullable=True) # Explicitly nullable
    gender = Column(Enum(GenderEnum), nullable=True) # Explicitly nullable
    profile_image_path = Column(String(255), nullable=True) # Explicitly nullable
    user_type = Column(Enum(UserTypeEnum), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    member = relationship("Member", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trainer = relationship("Trainer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    manager = relationship("Manager", back_populates="user", uselist=False, cascade="all, delete-orphan")
    created_schedules = relationship("WeeklySchedule", foreign_keys="[WeeklySchedule.created_by]", back_populates="creator", cascade="all, delete-orphan")


class Member(Base):
    __tablename__ = "members"

    member_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    weight = Column(Float, nullable=True)  # Changed to Float, explicitly nullable
    height = Column(Float, nullable=True)  # Changed to Float, explicitly nullable
    fitness_goal = Column(String(50), nullable=True) # Explicitly nullable
    fitness_level = Column(String(50), nullable=True) # Explicitly nullable
    health_conditions = Column(Text, nullable=True) # Explicitly nullable

    # Relationships
    user = relationship("User", back_populates="member")
    memberships = relationship("Membership", back_populates="member", cascade="all, delete-orphan")
    class_bookings = relationship("ClassBooking", back_populates="member", cascade="all, delete-orphan")
    saved_plans = relationship("MemberSavedPlan", back_populates="member", cascade="all, delete-orphan")
    custom_plan_requests = relationship("CustomPlanRequest", back_populates="member", cascade="all, delete-orphan")
    training_preferences = relationship("TrainingPreference", back_populates="member", cascade="all, delete-orphan")
    schedule_member_entries = relationship("ScheduleMember", back_populates="member", cascade="all, delete-orphan") # Renamed for clarity
    live_session_exercises = relationship("LiveSessionExercise", back_populates="member", cascade="all, delete-orphan")
    live_session_attendances = relationship("LiveSessionAttendance", back_populates="member", cascade="all, delete-orphan")
    training_cycles = relationship("TrainingCycle", back_populates="member", cascade="all, delete-orphan")


class Trainer(Base):
    __tablename__ = "trainers"

    trainer_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    specialization = Column(String(255), nullable=True) # Explicitly nullable
    bio = Column(Text, nullable=True) # Explicitly nullable
    certifications = Column(Text, nullable=True) # Explicitly nullable
    years_of_experience = Column(Integer, nullable=True) # Explicitly nullable

    # Relationships
    user = relationship("User", back_populates="trainer")
    classes = relationship("Class", back_populates="trainer")
    created_plans = relationship("TrainingPlan", back_populates="created_by_trainer")
    training_preferences_as_preferred = relationship("TrainingPreference", back_populates="trainer") # Relationship already in TrainingPreference
    weekly_schedules_assigned = relationship("WeeklySchedule", back_populates="trainer") # Relationship already in WeeklySchedule


class Manager(Base):
    __tablename__ = "managers"

    manager_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    department = Column(String(100), nullable=True) # Explicitly nullable
    hire_date = Column(Date, nullable=True) # Explicitly nullable

    # Relationships
    user = relationship("User", back_populates="manager")


# # backend/database/models/user.py
# from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Enum, DateTime, Text, Float
# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship
# import enum
# from ..base import Base

# class GenderEnum(enum.Enum):
#     Male = "Male"
#     Female = "Female"
#     Other = "Other"
#     PreferNotToSay = "Prefer not to say"

# class UserTypeEnum(enum.Enum):
#     member = "member"
#     trainer = "trainer"
#     manager = "manager"

# class User(Base):
#     __tablename__ = "users"

#     user_id = Column(Integer, primary_key=True, autoincrement=True)
#     firebase_uid = Column(String(128), unique=True, nullable=False) # TODO: Ensure this is enforced as not nullable
#     email = Column(String(255), unique=True, nullable=False)
#     first_name = Column(String(100), nullable=False)
#     last_name = Column(String(100), nullable=False)
#     phone = Column(String(20))
#     date_of_birth = Column(Date)
#     gender = Column(Enum(GenderEnum))
#     profile_image_path = Column(String(255))
#     user_type = Column(Enum(UserTypeEnum), nullable=False)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
#     is_active = Column(Boolean, default=True)

#     # Relationships
#     member = relationship("Member", back_populates="user", uselist=False, cascade="all, delete-orphan")
#     trainer = relationship("Trainer", back_populates="user", uselist=False, cascade="all, delete-orphan")
#     manager = relationship("Manager", back_populates="user", uselist=False, cascade="all, delete-orphan")
#     # Relationship for WeeklySchedule created_by
#     # created_schedules = relationship("WeeklySchedule", foreign_keys="[WeeklySchedule.created_by]", back_populates="creator") # This is handled by creator in WeeklySchedule


# class Member(Base):
#     __tablename__ = "members"

#     member_id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
#     weight = Column(Float)  # Changed to Float for more precision, e.g. 70.5 kg
#     height = Column(Float)  # Changed to Float, e.g. 170.5 cm
#     fitness_goal = Column(String(50))
#     fitness_level = Column(String(50))
#     health_conditions = Column(Text)

#     # Relationships
#     user = relationship("User", back_populates="member")
#     memberships = relationship("Membership", back_populates="member", cascade="all, delete-orphan")
#     class_bookings = relationship("ClassBooking", back_populates="member", cascade="all, delete-orphan")
#     saved_plans = relationship("MemberSavedPlan", back_populates="member", cascade="all, delete-orphan")
#     custom_plan_requests = relationship("CustomPlanRequest", back_populates="member", cascade="all, delete-orphan")
#     # TODO: Add relationship to TrainingPreference
#     training_preferences = relationship("TrainingPreference", back_populates="member", cascade="all, delete-orphan")
#     # TODO: Add relationship to ScheduleMember
#     scheduled_trainings = relationship("ScheduleMember", back_populates="member", cascade="all, delete-orphan")
#     # TODO: Add relationship to LiveSessionExercise
#     live_session_exercises = relationship("LiveSessionExercise", back_populates="member", cascade="all, delete-orphan")
#     # TODO: Add relationship to LiveSessionAttendance
#     live_session_attendances = relationship("LiveSessionAttendance", back_populates="member", cascade="all, delete-orphan")
#     # TODO: Add relationship to TrainingCycle
#     training_cycles = relationship("TrainingCycle", back_populates="member", cascade="all, delete-orphan")



# class Trainer(Base):
#     __tablename__ = "trainers"

#     trainer_id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
#     specialization = Column(String(255))
#     bio = Column(Text)
#     certifications = Column(Text)
#     years_of_experience = Column(Integer)

#     # Relationships
#     user = relationship("User", back_populates="trainer")
#     classes = relationship("Class", back_populates="trainer") # Assuming cascade delete handled by class if trainer is deleted
#     created_plans = relationship("TrainingPlan", back_populates="created_by_trainer")
#     # TODO: Add relationship for assigned training preferences
#     # assigned_preferences = relationship("TrainingPreference", back_populates="trainer") # This is already in TrainingPreference model
#     # TODO: Add relationship for assigned weekly schedules
#     # scheduled_sessions = relationship("WeeklySchedule", back_populates="trainer") # This is already in WeeklySchedule model


# class Manager(Base):
#     __tablename__ = "managers"

#     manager_id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
#     department = Column(String(100))
#     hire_date = Column(Date)

#     # Relationships
#     user = relationship("User", back_populates="manager")
