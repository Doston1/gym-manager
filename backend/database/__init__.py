from ...backend import engine, Base, get_db, SessionLocal

# Import all models to ensure they're registered with SQLAlchemy
from .models.user import User, Member, Trainer, Manager
from .models.membership import MembershipType, Membership
from .models.facility import Hall, GymHours
from .models.class_mgmt import ClassType, Class, ClassBooking
from .models.training import (
    TrainingPlan, TrainingPlanDay, Exercise, 
    TrainingDayExercise, MemberSavedPlan, CustomPlanRequest
)
from .models.analytics import FinancialTransaction, EmailNotification

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)