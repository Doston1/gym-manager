import enum
from sqlalchemy.orm import Session
from ..models.user import User, Member, Trainer, Manager, UserTypeEnum, GenderEnum

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.firebase_uid == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_firebase_uid(db: Session, firebase_uid: str):
    return db.query(User).filter(User.firebase_uid == firebase_uid).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user_data: dict):
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create the specific user type record based on user_type
    if db_user.user_type == UserTypeEnum.member:
        member = Member(user_id=db_user.user_id)
        db.add(member)
    elif db_user.user_type == UserTypeEnum.trainer:
        trainer = Trainer(user_id=db_user.user_id)
        db.add(trainer)
    elif db_user.user_type == UserTypeEnum.manager:
        manager = Manager(user_id=db_user.user_id)
        db.add(manager)
    
    db.commit()
    return db_user

def update_user(db: Session, user_id: int, user_data: dict):
    print(f'DEBUG: update_user: user_id={user_id}, user_data={user_data}')
    db_user = get_user_by_id(db, user_id)
    # if isinstance(user_data.get('gender'), GenderEnum):
    #     user_data['gender'] = user_data['gender'].value
    if db_user:
        for key, value in user_data.items():
            if isinstance(value, enum.Enum):
                value = value.value
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# Member-specific functions
def get_member_by_user_id(db: Session, user_id: int):
    return db.query(Member).filter(Member.user_id == user_id).first()

def update_member(db: Session, member_id: int, member_data: dict):
    db_member = db.query(Member).filter(Member.member_id == member_id).first()
    if db_member:
        for key, value in member_data.items():
            setattr(db_member, key, value)
        db.commit()
        db.refresh(db_member)
    return db_member

# Trainer-specific functions
def get_trainer_by_user_id(db: Session, user_id: int):
    return db.query(Trainer).filter(Trainer.user_id == user_id).first()

def get_all_trainers(db: Session):
    return db.query(Trainer).join(User).filter(User.is_active == True).all()

# Manager-specific functions
def get_manager_by_user_id(db: Session, user_id: int):
    return db.query(Manager).filter(Manager.user_id == user_id).first()