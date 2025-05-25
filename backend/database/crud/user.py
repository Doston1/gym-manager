import enum
from sqlalchemy.orm import Session
from ..models.user import User, Member, Trainer, Manager, UserTypeEnum, GenderEnum
from ..schemas.user import UserCreate # Added UserCreate for type hint

def get_user_by_id(db: Session, user_id: int): # This user_id is the DB PK
    return db.query(User).filter(User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_firebase_uid(db: Session, firebase_uid: str):
    return db.query(User).filter(User.firebase_uid == firebase_uid).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user_data: dict): # user_data is a dict from UserCreate schema
    # Convert string user_type to Enum if necessary
    if isinstance(user_data.get("user_type"), str):
        user_data["user_type"] = UserTypeEnum(user_data["user_type"])
    if isinstance(user_data.get("gender"), str): # Handle gender enum if passed as string
        try:
            user_data["gender"] = GenderEnum(user_data["gender"])
        except ValueError:
            user_data["gender"] = None # Or a default, or raise error

    db_user = User(**user_data)
    db.add(db_user)
    db.commit() # Commit to get user_id
    db.refresh(db_user)
    
    # Create the specific user type record based on user_type
    if db_user.user_type == UserTypeEnum.member:
        member_data = {"user_id": db_user.user_id}
        # Add default placeholder values for new members if desired
        member_data["weight"] = None # Or a default like 70.0
        member_data["height"] = None # Or 170.0
        member_data["fitness_goal"] = "General Fitness"
        member_data["fitness_level"] = "Beginner"
        member_data["health_conditions"] = "None specified"
        member = Member(**member_data)
        db.add(member)
    elif db_user.user_type == UserTypeEnum.trainer:
        trainer = Trainer(user_id=db_user.user_id)
        # Add default placeholder values for new trainers if desired
        trainer.specialization = "General Training"
        db.add(trainer)
    elif db_user.user_type == UserTypeEnum.manager:
        manager = Manager(user_id=db_user.user_id)
        db.add(manager)
    
    db.commit()
    db.refresh(db_user) # Refresh again to load related member/trainer/manager if needed by caller
    return db_user

def update_user(db: Session, user_id: int, user_data_dict: dict): # user_id is DB PK
    # The user_id coming from routes can be firebase_uid. We need to fetch by that.
    # Let's assume for now this function expects DB user_id.
    # If it's firebase_uid, the route should fetch user by firebase_uid first.
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    for key, value in user_data_dict.items():
        if hasattr(db_user, key):
            if isinstance(value, enum.Enum): # Convert enums to their values for DB
                setattr(db_user, key, value) # SQLAlchemy handles enums directly
            else:
                setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int): # user_id is DB PK
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user) # Cascades should handle related Member/Trainer/Manager records
        db.commit()
        return True
    return False

# Member-specific functions
def get_member_by_user_id(db: Session, user_id: int): # user_id is DB PK
    return db.query(Member).filter(Member.user_id == user_id).first()

def update_member_details(db: Session, firebase_uid_or_user_id: str, member_data_dict: dict):
    # Determine if identifier is firebase_uid or user_id (int)
    user = None
    try:
        # Try to interpret as int (user_id)
        db_user_id = int(firebase_uid_or_user_id)
        user = get_user_by_id(db, db_user_id)
    except ValueError:
        # Interpret as firebase_uid (str)
        user = get_user_by_firebase_uid(db, firebase_uid_or_user_id)

    if not user or not user.member:
        return None # User or member profile not found
    
    db_member = user.member
    for key, value in member_data_dict.items():
        if hasattr(db_member, key):
            setattr(db_member, key, value)
    db.commit()
    db.refresh(db_member)
    return db_member


# Trainer-specific functions
def get_trainer_by_user_id(db: Session, user_id: int): # user_id is DB PK
    return db.query(Trainer).filter(Trainer.user_id == user_id).first()

def get_all_trainers(db: Session):
    return db.query(Trainer).join(User).filter(User.is_active == True).all() # TODO: Ensure this join is correct

# Manager-specific functions
def get_manager_by_user_id(db: Session, user_id: int): # user_id is DB PK
    return db.query(Manager).filter(Manager.user_id == user_id).first()

def get_all_active_trainers_for_select(db: Session) -> list[dict]:
    trainers = db.query(User.user_id, User.first_name, User.last_name, Trainer.trainer_id).\
        join(Trainer, User.user_id == Trainer.user_id).\
        filter(User.is_active == True).all()
    return [{"label": f"{t.first_name} {t.last_name}", "value": t.trainer_id} for t in trainers]


# ---------------------------------------------------------------------------------------------------------

# import enum
# from sqlalchemy.orm import Session
# from ..models.user import User, Member, Trainer, Manager, UserTypeEnum, GenderEnum

# def get_user_by_id(db: Session, user_id: int):
#     return db.query(User).filter(User.firebase_uid == user_id).first()

# def get_user_by_email(db: Session, email: str):
#     return db.query(User).filter(User.email == email).first()

# def get_user_by_firebase_uid(db: Session, firebase_uid: str):
#     return db.query(User).filter(User.firebase_uid == firebase_uid).first()

# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(User).offset(skip).limit(limit).all()

# def create_user(db: Session, user_data: dict):
#     db_user = User(**user_data)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
    
#     # Create the specific user type record based on user_type
#     if db_user.user_type == UserTypeEnum.member:
#         member = Member(user_id=db_user.user_id)
#         db.add(member)
#     elif db_user.user_type == UserTypeEnum.trainer:
#         trainer = Trainer(user_id=db_user.user_id)
#         db.add(trainer)
#     elif db_user.user_type == UserTypeEnum.manager:
#         manager = Manager(user_id=db_user.user_id)
#         db.add(manager)
    
#     db.commit()
#     return db_user

# def update_user(db: Session, user_id: int, user_data: dict):
#     print(f'DEBUG: update_user: user_id={user_id}, user_data={user_data}')
#     db_user = get_user_by_id(db, user_id)
#     # if isinstance(user_data.get('gender'), GenderEnum):
#     #     user_data['gender'] = user_data['gender'].value
#     if db_user:
#         for key, value in user_data.items():
#             if isinstance(value, enum.Enum):
#                 value = value.value
#             setattr(db_user, key, value)
#         db.commit()
#         db.refresh(db_user)
#     return db_user

# def delete_user(db: Session, user_id: int):
#     db_user = get_user_by_id(db, user_id)
#     if db_user:
#         db.delete(db_user)
#         db.commit()
#         return True
#     return False

# # Member-specific functions
# def get_member_by_user_id(db: Session, user_id: int):
#     return db.query(Member).filter(Member.user_id == user_id).first()

# def update_member(db: Session, member_id: int, member_data: dict):
#     db_member = db.query(Member).filter(Member.member_id == member_id).first()
#     if db_member:
#         for key, value in member_data.items():
#             setattr(db_member, key, value)
#         db.commit()
#         db.refresh(db_member)
#     return db_member

# # Trainer-specific functions
# def get_trainer_by_user_id(db: Session, user_id: int):
#     return db.query(Trainer).filter(Trainer.user_id == user_id).first()

# def get_all_trainers(db: Session):
#     return db.query(Trainer).join(User).filter(User.is_active == True).all()

# # Manager-specific functions
# def get_manager_by_user_id(db: Session, user_id: int):
#     return db.query(Manager).filter(Manager.user_id == user_id).first()