from sqlalchemy.orm import Session
from ..models.membership import Membership, MembershipType

# MembershipType-specific functions
def get_membership_type_by_id(db: Session, membership_type_id: int):
    return db.query(MembershipType).filter(MembershipType.membership_type_id == membership_type_id).first()

def get_all_membership_types(db: Session):
    return db.query(MembershipType).all()

def create_membership_type(db: Session, membership_type_data: dict):
    db_membership_type = MembershipType(**membership_type_data)
    db.add(db_membership_type)
    db.commit()
    db.refresh(db_membership_type)
    return db_membership_type

def update_membership_type(db: Session, membership_type_id: int, membership_type_data: dict):
    db_membership_type = get_membership_type_by_id(db, membership_type_id)
    if db_membership_type:
        for key, value in membership_type_data.items():
            setattr(db_membership_type, key, value)
        db.commit()
        db.refresh(db_membership_type)
    return db_membership_type

def delete_membership_type(db: Session, membership_type_id: int):
    db_membership_type = get_membership_type_by_id(db, membership_type_id)
    if db_membership_type:
        db.delete(db_membership_type)
        db.commit()
        return True
    return False

# Membership-specific functions
def get_membership_by_id(db: Session, membership_id: int):
    return db.query(Membership).filter(Membership.membership_id == membership_id).first()

def get_memberships_by_member_id(db: Session, member_id: int):
    return db.query(Membership).filter(Membership.member_id == member_id).all()

def create_membership(db: Session, membership_data: dict):
    db_membership = Membership(**membership_data)
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

def update_membership(db: Session, membership_id: int, membership_data: dict):
    db_membership = get_membership_by_id(db, membership_id)
    if db_membership:
        for key, value in membership_data.items():
            setattr(db_membership, key, value)
        db.commit()
        db.refresh(db_membership)
    return db_membership

def delete_membership(db: Session, membership_id: int):
    db_membership = get_membership_by_id(db, membership_id)
    if db_membership:
        db.delete(db_membership)
        db.commit()
        return True
    return False