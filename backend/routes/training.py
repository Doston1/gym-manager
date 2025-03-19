from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models.training import TrainingPlan
from backend.database.schemas.training import (
    TrainingPlanCreate,
    TrainingPlanResponse,
    TrainingPlanUpdate,
)
from typing import List

router = APIRouter(prefix="/training-plans", tags=["Training Plans"])


# ✅ Get all training plans
@router.get("/", response_model=List[TrainingPlanResponse])
def get_all_training_plans(db: Session = Depends(get_db)):
    plans = db.query(TrainingPlan).all()
    return plans


# ✅ Get a specific training plan by ID
@router.get("/{plan_id}", response_model=TrainingPlanResponse)
def get_training_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(TrainingPlan).filter(TrainingPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Training plan not found")
    return plan


# ✅ Create a new training plan
@router.post("/", response_model=TrainingPlanResponse)
def create_training_plan(plan_data: TrainingPlanCreate, db: Session = Depends(get_db)):
    new_plan = TrainingPlan(**plan_data.dict())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan


# ✅ Update an existing training plan
@router.put("/{plan_id}", response_model=TrainingPlanResponse)
def update_training_plan(plan_id: int, updated_data: TrainingPlanUpdate, db: Session = Depends(get_db)):
    plan = db.query(TrainingPlan).filter(TrainingPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Training plan not found")
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan


# ✅ Delete a training plan
@router.delete("/{plan_id}", response_model=dict)
def delete_training_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(TrainingPlan).filter(TrainingPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Training plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Training plan deleted successfully"}