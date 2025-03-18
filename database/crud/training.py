from sqlalchemy.orm import Session
from ..models.training import TrainingPlan, TrainingPlanDay, Exercise

# TrainingPlan-specific functions
def get_training_plan_by_id(db: Session, plan_id: int):
    return db.query(TrainingPlan).filter(TrainingPlan.plan_id == plan_id).first()

def create_training_plan(db: Session, plan_data: dict):
    db_plan = TrainingPlan(**plan_data)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_training_plan(db: Session, plan_id: int):
    db_plan = get_training_plan_by_id(db, plan_id)
    if db_plan:
        db.delete(db_plan)
        db.commit()
        return True
    return False

# TrainingPlanDay-specific functions
def create_training_plan_day(db: Session, day_data: dict):
    db_day = TrainingPlanDay(**day_data)
    db.add(db_day)
    db.commit()
    db.refresh(db_day)
    return db_day

# Exercise-specific functions
def create_exercise(db: Session, exercise_data: dict):
    db_exercise = Exercise(**exercise_data)
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise