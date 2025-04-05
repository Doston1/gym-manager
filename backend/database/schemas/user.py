from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
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

# Base schema for User
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    # gender: Optional[GenderEnum]
    gender: Optional[str]
    profile_image_path: Optional[str]
    # user_type: UserTypeEnum
    user_type : str
    is_active: Optional[bool] = True

# Schema for creating a new user
class UserCreate(UserBase):
    firebase_uid: Optional[str]  # Firebase UID is optional during creation

# Schema for updating an existing user
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    profile_image_path: Optional[str] = None
    is_active: Optional[bool] = None

# Schema for returning user data
class UserResponse(UserBase):
    user_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

# class Member():
#     member_id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
#     weight = Column(Integer)  # in kg
#     height = Column(Integer)  # in cm
#     fitness_goal = Column(String(50))
#     fitness_level = Column(String(50))
#     health_conditions = Column(Text)


# class Trainer():
#     trainer_id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
#     specialization = Column(String(255))
#     bio = Column(Text)
#     certifications = Column(Text)
#     years_of_experience = Column(Integer)

# class Manager():
#     manager_id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
#     department = Column(String(100))
#     hire_date = Column(Date)