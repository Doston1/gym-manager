from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models.user import User
from backend.database.schemas.user import UserCreate, UserResponse, UserUpdate
from backend.database.crud.user import create_user, get_user_by_id, update_user, delete_user


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# def get_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.user_id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

@router.post("/", response_model=UserResponse)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, user.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user_endpoint(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = update_user(db, user_id, user_update.dict(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# def update_user(user_id: int, updated_data: dict, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.user_id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     for key, value in updated_data.items():
#         setattr(user, key, value)
#     db.commit()
#     db.refresh(user)
#     return user


@router.delete("/{user_id}")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    if not delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
 
# def delete_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.user_id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     db.delete(user)
#     db.commit()
#     return {"message": "User deleted successfully"}