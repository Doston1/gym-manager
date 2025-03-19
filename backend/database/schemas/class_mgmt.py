from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal
from backend.database.models.class_mgmt import (
    DifficultyLevelEnum,
    ClassStatusEnum,
    BookingPaymentStatusEnum,
    AttendanceStatusEnum,
)

# Base schema for ClassType
class ClassTypeBase(BaseModel):
    name: str
    description: Optional[str]
    duration_minutes: int
    difficulty_level: DifficultyLevelEnum = DifficultyLevelEnum.AllLevels
    equipment_needed: Optional[str]
    default_max_participants: Optional[int]
    default_price: Decimal
    is_active: bool = True


# Schema for creating a new ClassType
class ClassTypeCreate(ClassTypeBase):
    pass


# Schema for returning ClassType data
class ClassTypeResponse(ClassTypeBase):
    class_type_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Base schema for Class
class ClassBase(BaseModel):
    class_type_id: int
    trainer_id: int
    hall_id: int
    date: date
    start_time: time
    end_time: time
    max_participants: int
    current_participants: int = 0
    price: Decimal
    status: ClassStatusEnum = ClassStatusEnum.Scheduled
    notes: Optional[str]


# Schema for creating a new Class
class ClassCreate(ClassBase):
    pass


# Schema for returning Class data
class ClassResponse(ClassBase):
    class_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Base schema for ClassBooking
class ClassBookingBase(BaseModel):
    class_id: int
    member_id: int
    payment_status: BookingPaymentStatusEnum
    amount_paid: Optional[Decimal]
    attendance_status: AttendanceStatusEnum = AttendanceStatusEnum.NotAttended
    cancellation_date: Optional[datetime]
    cancellation_reason: Optional[str]
    email_notification_sent: bool = False


# Schema for creating a new ClassBooking
class ClassBookingCreate(ClassBookingBase):
    pass


# Schema for returning ClassBooking data
class ClassBookingResponse(ClassBookingBase):
    booking_id: int
    booking_date: datetime

    class Config:
        orm_mode = True