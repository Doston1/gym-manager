from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models.training import TrainingPlan

router = APIRouter(prefix="/training-plans", tags=["Training Plans"])

@router.get("/")
def get_all_training_plans(db: Session = Depends(get_db)):
    return db.query(TrainingPlan).all()

@router.get("/{plan_id}")
def get_training_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(TrainingPlan).filter(TrainingPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Training plan not found")
    return plan

@router.post("/")
def create_training_plan(plan: TrainingPlan, db: Session = Depends(get_db)):
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.put("/{plan_id}")
def update_training_plan(plan_id: int, updated_data: dict, db: Session = Depends(get_db)):
    plan = db.query(TrainingPlan).filter(TrainingPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Training plan not found")
    for key, value in updated_data.items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan

@router.delete("/{plan_id}")
def delete_training_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(TrainingPlan).filter(TrainingPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Training plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Training plan deleted successfully"}
