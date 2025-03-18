from sqlalchemy.orm import Session
from ..models.class_mgmt import Class, ClassType, ClassBooking

# ClassType-specific functions
def get_class_type_by_id(db: Session, class_type_id: int):
    return db.query(ClassType).filter(ClassType.class_type_id == class_type_id).first()

def get_all_class_types(db: Session):
    return db.query(ClassType).all()

def create_class_type(db: Session, class_type_data: dict):
    db_class_type = ClassType(**class_type_data)
    db.add(db_class_type)
    db.commit()
    db.refresh(db_class_type)
    return db_class_type

def update_class_type(db: Session, class_type_id: int, class_type_data: dict):
    db_class_type = get_class_type_by_id(db, class_type_id)
    if db_class_type:
        for key, value in class_type_data.items():
            setattr(db_class_type, key, value)
        db.commit()
        db.refresh(db_class_type)
    return db_class_type

def delete_class_type(db: Session, class_type_id: int):
    db_class_type = get_class_type_by_id(db, class_type_id)
    if db_class_type:
        db.delete(db_class_type)
        db.commit()
        return True
    return False

# Class-specific functions
def get_class_by_id(db: Session, class_id: int):
    return db.query(Class).filter(Class.class_id == class_id).first()

def get_classes_by_trainer_id(db: Session, trainer_id: int):
    return db.query(Class).filter(Class.trainer_id == trainer_id).all()

def create_class(db: Session, class_data: dict):
    db_class = Class(**class_data)
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

def update_class(db: Session, class_id: int, class_data: dict):
    db_class = get_class_by_id(db, class_id)
    if db_class:
        for key, value in class_data.items():
            setattr(db_class, key, value)
        db.commit()
        db.refresh(db_class)
    return db_class

def delete_class(db: Session, class_id: int):
    db_class = get_class_by_id(db, class_id)
    if db_class:
        db.delete(db_class)
        db.commit()
        return True
    return False

# ClassBooking-specific functions
def get_class_booking_by_id(db: Session, booking_id: int):
    return db.query(ClassBooking).filter(ClassBooking.booking_id == booking_id).first()

def create_class_booking(db: Session, booking_data: dict):
    db_booking = ClassBooking(**booking_data)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def delete_class_booking(db: Session, booking_id: int):
    db_booking = get_class_booking_by_id(db, booking_id)
    if db_booking:
        db.delete(db_booking)
        db.commit()
        return True
    return False