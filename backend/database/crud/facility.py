from sqlalchemy.orm import Session
from ..models.facility import Hall, GymHours

# Hall-specific functions
def get_hall_by_id(db: Session, hall_id: int):
    return db.query(Hall).filter(Hall.hall_id == hall_id).first()

def get_all_halls(db: Session):
    return db.query(Hall).all()

def create_hall(db: Session, hall_data: dict):
    db_hall = Hall(**hall_data)
    db.add(db_hall)
    db.commit()
    db.refresh(db_hall)
    return db_hall

def update_hall(db: Session, hall_id: int, hall_data: dict):
    db_hall = get_hall_by_id(db, hall_id)
    if db_hall:
        for key, value in hall_data.items():
            setattr(db_hall, key, value)
        db.commit()
        db.refresh(db_hall)
    return db_hall

def delete_hall(db: Session, hall_id: int):
    db_hall = get_hall_by_id(db, hall_id)
    if db_hall:
        db.delete(db_hall)
        db.commit()
        return True
    return False

# GymHours-specific functions
def get_gym_hours_by_id(db: Session, hours_id: int):
    return db.query(GymHours).filter(GymHours.hours_id == hours_id).first()

def get_all_gym_hours(db: Session):
    return db.query(GymHours).all()

def create_gym_hours(db: Session, gym_hours_data: dict):
    db_gym_hours = GymHours(**gym_hours_data)
    db.add(db_gym_hours)
    db.commit()
    db.refresh(db_gym_hours)
    return db_gym_hours

def update_gym_hours(db: Session, hours_id: int, gym_hours_data: dict):
    db_gym_hours = get_gym_hours_by_id(db, hours_id)
    if db_gym_hours:
        for key, value in gym_hours_data.items():
            setattr(db_gym_hours, key, value)
        db.commit()
        db.refresh(db_gym_hours)
    return db_gym_hours

def delete_gym_hours(db: Session, hours_id: int):
    db_gym_hours = get_gym_hours_by_id(db, hours_id)
    if db_gym_hours:
        db.delete(db_gym_hours)
        db.commit()
        return True
    return False