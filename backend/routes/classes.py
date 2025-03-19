from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.schemas.class_mgmt import (
    ClassTypeCreate,
    ClassTypeResponse,
    ClassCreate,
    ClassResponse,
    ClassBookingCreate,
    ClassBookingResponse,
)
from backend.database.crud.class_mgmt import (
    get_all_classes as crud_get_all_classes,
    get_class_by_id as crud_get_class_by_id,
    create_class as crud_create_class,
    update_class as crud_update_class,
    delete_class as crud_delete_class,
    create_class_booking as crud_create_class_booking,
)

router = APIRouter(prefix="/classes", tags=["Classes"])


# ✅ Get all classes
@router.get("/", response_model=list[ClassResponse])
def get_all_classes(db: Session = Depends(get_db)):
    return crud_get_all_classes(db)


# ✅ Get a specific class by ID
@router.get("/{class_id}", response_model=ClassResponse)
def get_class(class_id: int, db: Session = Depends(get_db)):
    gym_class = crud_get_class_by_id(db, class_id)
    if not gym_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return gym_class


# ✅ Create a new class
@router.post("/", response_model=ClassResponse)
def create_class(gym_class: ClassCreate, db: Session = Depends(get_db)):
    return crud_create_class(db, gym_class)


# ✅ Update an existing class
@router.put("/{class_id}", response_model=ClassResponse)
def update_class(class_id: int, updated_data: ClassCreate, db: Session = Depends(get_db)):
    updated_class = crud_update_class(db, class_id, updated_data)
    if not updated_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return updated_class


# ✅ Delete a class
@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    if not crud_delete_class(db, class_id):
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted successfully"}


# ✅ Create a class booking
@router.post("/bookings", response_model=ClassBookingResponse)
def create_class_booking(booking: ClassBookingCreate, db: Session = Depends(get_db)):
    return crud_create_class_booking(db, booking)