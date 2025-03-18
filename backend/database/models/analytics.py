from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Text, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ....backend import Base

class TransactionTypeEnum(enum.Enum):
    MembershipFee = "Membership Fee"
    ClassBooking = "Class Booking"
    CancellationFee = "Cancellation Fee"
    Refund = "Refund"
    Other = "Other"

class PaymentMethodEnum(enum.Enum):
    CreditCard = "Credit Card"
    DebitCard = "Debit Card"
    Cash = "Cash"
    BankTransfer = "Bank Transfer"
    Other = "Other"

class TransactionStatusEnum(enum.Enum):
    Pending = "Pending"
    Completed = "Completed"
    Failed = "Failed"
    Refunded = "Refunded"

class NotificationTypeEnum(enum.Enum):
    ClassBooking = "Class Booking"
    ClassCancellation = "Class Cancellation"
    Membership = "Membership"
    CustomPlan = "Custom Plan"
    General = "General"

class NotificationStatusEnum(enum.Enum):
    Sent = "Sent"
    Failed = "Failed"
    Pending = "Pending"

class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"
    
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))
    transaction_type = Column(Enum(TransactionTypeEnum), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethodEnum), nullable=False)
    transaction_date = Column(DateTime, server_default=func.now())
    status = Column(Enum(TransactionStatusEnum), default=TransactionStatusEnum.Pending)
    reference_id = Column(String(255))
    notes = Column(Text)
    
    # Relationships
    member = relationship("Member")


class EmailNotification(Base):
    __tablename__ = "email_notifications"
    
    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, server_default=func.now())
    status = Column(Enum(NotificationStatusEnum), default=NotificationStatusEnum.Pending)
    related_type = Column(Enum(NotificationTypeEnum), nullable=False)
    related_id = Column(Integer)
    
    # Relationships
    user = relationship("User")