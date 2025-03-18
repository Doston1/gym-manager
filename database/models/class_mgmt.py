from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Enum, DateTime, Text, Numeric, Time, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..base import Base

class DifficultyLevelEnum(enum.Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Advanced = "Advanced"
    AllLevels = "All Levels"

class ClassStatusEnum(enum.Enum):
    Scheduled = "Scheduled"
    Cancelled = "Cancelled"
    Completed = "Completed"
    Rescheduled = "Rescheduled"

class BookingPaymentStatusEnum(enum.Enum):
    Pending = "Pending"
    Paid = "Paid"
    Free = "Free"
    Cancelled = "Cancelled"

class AttendanceStatusEnum(enum.Enum):
    NotAttended = "Not Attended"
    Attended = "Attended"
    Cancelled = "Cancelled"
    NoShow = "No Show"

class ClassType(Base):
    __tablename__ = "class_types"
    
    class_type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer, nullable=False)
    difficulty_level = Column(Enum(DifficultyLevelEnum), default=DifficultyLevelEnum.AllLevels)
    equipment_needed = Column(Text)
    default_max_participants = Column(Integer)
    default_price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    classes = relationship("Class", back_populates="class_type")


class Class(Base):
    __tablename__ = "classes"
    
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    class_type_id = Column(Integer, ForeignKey("class_types.class_type_id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.trainer_id"), nullable=False)
    hall_id = Column(Integer, ForeignKey("halls.hall_id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_participants = Column(Integer, nullable=False)
    current_participants = Column(Integer, default=0)
    price = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(ClassStatusEnum), default=ClassStatusEnum.Scheduled)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    class_type = relationship("ClassType", back_populates="classes")
    trainer = relationship("Trainer", back_populates="classes")
    hall = relationship("Hall", back_populates="classes")
    bookings = relationship("ClassBooking", back_populates="class_")
    
    # Indexes
    __table_args__ = (
        Index('idx_class_date_time', 'date', 'start_time'),
    )


class ClassBooking(Base):
    __tablename__ = "class_bookings"
    
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.class_id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    booking_date = Column(DateTime, server_default=func.now())
    payment_status = Column(Enum(BookingPaymentStatusEnum), nullable=False)
    amount_paid = Column(Numeric(10, 2))
    attendance_status = Column(Enum(AttendanceStatusEnum), default=AttendanceStatusEnum.NotAttended)
    cancellation_date = Column(DateTime)
    cancellation_reason = Column(Text)
    email_notification_sent = Column(Boolean, default=False)
    
    # Relationships
    class_ = relationship("Class", back_populates="bookings")
    member = relationship("Member", back_populates="class_bookings")
    
    # Unique constraint to prevent double bookings
    __table_args__ = (
        Index('unique_booking', 'class_id', 'member_id', unique=True),
    )