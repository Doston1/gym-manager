from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models.user import User
from backend.database.schemas.user import UserCreate, UserResponse, UserUpdate
from backend.database.crud.user import create_user, get_user_by_id, update_user, delete_user


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: str, db: Session = Depends(get_db)):  # Changed user_id to str
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, user.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user_id: str, request: Request, db: Session = Depends(get_db)):  # Ensure user_id is str
    print(f'DEBUGL update_user_endpoint: user_id={user_id}')
    try:
        data = await request.json()
        print(f"🔥 RAW REQUEST BODY: {data}")
        validated = UserUpdate(**data)
    except Exception as e:
        print(f"❌ Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    user = update_user(db, user_id, validated.dict(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user_endpoint(user_id: str, db: Session = Depends(get_db)):  # Changed user_id to str
    if not delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
