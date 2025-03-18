from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Enum, DateTime, Text, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ....backend import Base

class PaymentStatusEnum(enum.Enum):
    Pending = "Pending"
    Paid = "Paid"
    Failed = "Failed"
    Cancelled = "Cancelled"

class MembershipType(Base):
    __tablename__ = "membership_types"
    
    membership_type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price_monthly = Column(Numeric(10, 2), nullable=False)
    price_quarterly = Column(Numeric(10, 2))
    price_yearly = Column(Numeric(10, 2))
    max_classes_per_week = Column(Integer)
    custom_plans_period = Column(Integer)  # Number of weeks between allowed custom plans
    unlimited_custom_plans = Column(Boolean, default=False)
    class_booking_discount = Column(Numeric(5, 2), default=0)  # Percentage discount on class bookings
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    memberships = relationship("Membership", back_populates="membership_type")


class Membership(Base):
    __tablename__ = "memberships"
    
    membership_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    membership_type_id = Column(Integer, ForeignKey("membership_types.membership_type_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    payment_status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.Pending)
    auto_renew = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    member = relationship("Member", back_populates="memberships")
    membership_type = relationship("MembershipType", back_populates="memberships")