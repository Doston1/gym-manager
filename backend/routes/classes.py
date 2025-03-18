from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models.class_mgmt import Class

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.get("/")
def get_all_classes(db: Session = Depends(get_db)):
    return db.query(Class).all()

@router.get("/{class_id}")
def get_class(class_id: int, db: Session = Depends(get_db)):
    gym_class = db.query(Class).filter(Class.class_id == class_id).first()
    if not gym_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return gym_class

@router.post("/")
def create_class(gym_class: Class, db: Session = Depends(get_db)):
    db.add(gym_class)
    db.commit()
    db.refresh(gym_class)
    return gym_class

@router.put("/{class_id}")
def update_class(class_id: int, updated_data: dict, db: Session = Depends(get_db)):
    gym_class = db.query(Class).filter(Class.class_id == class_id).first()
    if not gym_class:
        raise HTTPException(status_code=404, detail="Class not found")
    for key, value in updated_data.items():
        setattr(gym_class, key, value)
    db.commit()
    db.refresh(gym_class)
    return gym_class

@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    gym_class = db.query(Class).filter(Class.class_id == class_id).first()
    if not gym_class:
        raise HTTPException(status_code=404, detail="Class not found")
    db.delete(gym_class)
    db.commit()
    return {"message": "Class deleted successfully"}
