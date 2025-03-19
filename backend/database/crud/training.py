from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.training import TrainingPlan, TrainingPlanDay, Exercise, TrainingDayExercise, MemberSavedPlan, CustomPlanRequest


# ✅ TrainingPlan-specific functions
def get_training_plan_by_id(db: Session, plan_id: int):
    return db.query(TrainingPlan).filter(TrainingPlan.plan_id == plan_id).first()


def get_all_training_plans(db: Session):
    return db.query(TrainingPlan).all()


def create_training_plan(db: Session, plan_data: dict):
    db_plan = TrainingPlan(**plan_data)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def update_training_plan(db: Session, plan_id: int, updated_data: dict):
    db_plan = get_training_plan_by_id(db, plan_id)
    if not db_plan:
        return None
    for key, value in updated_data.items():
        setattr(db_plan, key, value)
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


# ✅ TrainingPlanDay-specific functions
def get_training_plan_day_by_id(db: Session, day_id: int):
    return db.query(TrainingPlanDay).filter(TrainingPlanDay.day_id == day_id).first()


def create_training_plan_day(db: Session, day_data: dict):
    db_day = TrainingPlanDay(**day_data)
    db.add(db_day)
    db.commit()
    db.refresh(db_day)
    return db_day


def delete_training_plan_day(db: Session, day_id: int):
    db_day = get_training_plan_day_by_id(db, day_id)
    if db_day:
        db.delete(db_day)
        db.commit()
        return True
    return False


# ✅ Exercise-specific functions
def get_exercise_by_id(db: Session, exercise_id: int):
    return db.query(Exercise).filter(Exercise.exercise_id == exercise_id).first()


def create_exercise(db: Session, exercise_data: dict):
    db_exercise = Exercise(**exercise_data)
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def delete_exercise(db: Session, exercise_id: int):
    db_exercise = get_exercise_by_id(db, exercise_id)
    if db_exercise:
        db.delete(db_exercise)
        db.commit()
        return True
    return False


# ✅ TrainingDayExercise-specific functions
def get_training_day_exercise_by_id(db: Session, id: int):
    return db.query(TrainingDayExercise).filter(TrainingDayExercise.id == id).first()


def create_training_day_exercise(db: Session, exercise_data: dict):
    db_day_exercise = TrainingDayExercise(**exercise_data)
    db.add(db_day_exercise)
    db.commit()
    db.refresh(db_day_exercise)
    return db_day_exercise


def delete_training_day_exercise(db: Session, id: int):
    db_day_exercise = get_training_day_exercise_by_id(db, id)
    if db_day_exercise:
        db.delete(db_day_exercise)
        db.commit()
        return True
    return False


# ✅ MemberSavedPlan-specific functions
def get_member_saved_plan_by_id(db: Session, id: int):
    return db.query(MemberSavedPlan).filter(MemberSavedPlan.id == id).first()


def create_member_saved_plan(db: Session, saved_plan_data: dict):
    try:
        db_saved_plan = MemberSavedPlan(**saved_plan_data)
        db.add(db_saved_plan)
        db.commit()
        db.refresh(db_saved_plan)
        return db_saved_plan
    except IntegrityError:
        db.rollback()
        raise ValueError("This member has already saved this plan.")


def delete_member_saved_plan(db: Session, id: int):
    db_saved_plan = get_member_saved_plan_by_id(db, id)
    if db_saved_plan:
        db.delete(db_saved_plan)
        db.commit()
        return True
    return False


# ✅ CustomPlanRequest-specific functions
def get_custom_plan_request_by_id(db: Session, request_id: int):
    return db.query(CustomPlanRequest).filter(CustomPlanRequest.request_id == request_id).first()


def create_custom_plan_request(db: Session, request_data: dict):
    db_request = CustomPlanRequest(**request_data)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def update_custom_plan_request(db: Session, request_id: int, updated_data: dict):
    db_request = get_custom_plan_request_by_id(db, request_id)
    if not db_request:
        return None
    for key, value in updated_data.items():
        setattr(db_request, key, value)
    db.commit()
    db.refresh(db_request)
    return db_request


def delete_custom_plan_request(db: Session, request_id: int):
    db_request = get_custom_plan_request_by_id(db, request_id)
    if db_request:
        db.delete(db_request)
        db.commit()
        return True
    return False