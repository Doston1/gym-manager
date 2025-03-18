from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Enum, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ....backend import Base

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
    firebase_uid = Column(String(128), unique=True)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    gender = Column(Enum(GenderEnum))
    profile_image_path = Column(String(255))
    user_type = Column(Enum(UserTypeEnum), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    member = relationship("Member", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trainer = relationship("Trainer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    manager = relationship("Manager", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Member(Base):
    __tablename__ = "members"
    
    member_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    weight = Column(Integer)  # in kg
    height = Column(Integer)  # in cm
    fitness_goal = Column(String(50))
    fitness_level = Column(String(50))
    health_conditions = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="member")
    memberships = relationship("Membership", back_populates="member")
    class_bookings = relationship("ClassBooking", back_populates="member")
    saved_plans = relationship("MemberSavedPlan", back_populates="member")
    custom_plan_requests = relationship("CustomPlanRequest", back_populates="member")


class Trainer(Base):
    __tablename__ = "trainers"
    
    trainer_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    specialization = Column(String(255))
    bio = Column(Text)
    certifications = Column(Text)
    years_of_experience = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="trainer")
    classes = relationship("Class", back_populates="trainer")
    created_plans = relationship("TrainingPlan", back_populates="created_by_trainer")


class Manager(Base):
    __tablename__ = "managers"
    
    manager_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    department = Column(String(100))
    hire_date = Column(Date)
    
    # Relationships
    user = relationship("User", back_populates="manager")