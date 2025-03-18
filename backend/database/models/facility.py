from sqlalchemy import Column, Integer, String, Boolean, Time, Enum, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ....backend import Base

class DayOfWeekEnum(enum.Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    Sunday = "Sunday"

class Hall(Base):
    __tablename__ = "halls"
    
    hall_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    max_capacity = Column(Integer, nullable=False)
    location = Column(String(255))
    equipment_available = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    classes = relationship("Class", back_populates="hall")


class GymHours(Base):
    __tablename__ = "gym_hours"
    
    hours_id = Column(Integer, primary_key=True, autoincrement=True)
    day_of_week = Column(Enum(DayOfWeekEnum), nullable=False, unique=True)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    is_closed = Column(Boolean, default=False)
    special_note = Column(Text)
    is_holiday = Column(Boolean, default=False)