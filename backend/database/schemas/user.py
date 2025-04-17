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
    gender: Optional[str]
    profile_image_path: Optional[str]
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

# Member schemas
class MemberBase(BaseModel):
    weight: Optional[float]
    height: Optional[float]
    fitness_goal: Optional[str]
    fitness_level: Optional[str]
    health_conditions: Optional[str]

class MemberCreate(MemberBase):
    user_id: int

class MemberUpdate(MemberBase):
    pass

class MemberResponse(MemberBase):
    member_id: int
    user_id: int
    user: UserResponse

    class Config:
        orm_mode = True

# Trainer schemas
class TrainerBase(BaseModel):
    specialization: Optional[str]
    bio: Optional[str]
    certifications: Optional[str]
    years_of_experience: Optional[int]

class TrainerCreate(TrainerBase):
    user_id: int

class TrainerUpdate(TrainerBase):
    pass

class TrainerResponse(TrainerBase):
    trainer_id: int
    user_id: int
    user: UserResponse

    class Config:
        orm_mode = True

# Manager schemas
class ManagerBase(BaseModel):
    department: Optional[str]
    hire_date: Optional[date]

class ManagerCreate(ManagerBase):
    user_id: int

class ManagerUpdate(ManagerBase):
    pass

class ManagerResponse(ManagerBase):
    manager_id: int
    user_id: int
    user: UserResponse

    class Config:
        orm_mode = True