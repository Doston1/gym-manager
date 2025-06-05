# In backend/routes/training.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.database.base import get_db_cursor
from backend.database.crud import training as crud_training # Assuming crud_training is refactored
# from backend.auth import get_current_user_data # For protected routes

router = APIRouter(prefix="/training", tags=["Training"]) # Changed prefix for clarity

# === TrainingPlan Routes ===
@router.get("/plans/", ) # Removed response_model
def get_all_training_plans_route(db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    plans = crud_training.get_all_training_plans(db_conn, cursor)
    return plans

@router.get("/plans/{plan_id}")
def get_training_plan_route(plan_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    plan = crud_training.get_training_plan_by_id(db_conn, cursor, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Training plan not found")
    return plan

@router.post("/plans/", status_code=status.HTTP_201_CREATED)
async def create_training_plan_route(request: Request, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    payload = await request.json()
    # Validation is handled in CRUD
    new_plan = crud_training.create_training_plan(db_conn, cursor, payload)
    return new_plan

@router.put("/plans/{plan_id}")
async def update_training_plan_route(plan_id: int, request: Request, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    payload = await request.json()
    updated_plan = crud_training.update_training_plan(db_conn, cursor, plan_id, payload)
    if not updated_plan:
        raise HTTPException(status_code=404, detail="Training plan not found or no update performed")
    return updated_plan

@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_plan_route(plan_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    if not crud_training.delete_training_plan(db_conn, cursor, plan_id):
        raise HTTPException(status_code=404, detail="Training plan not found")
    return None

# ... Continue for all other sub-entities in training.py (TrainingPlanDay, Exercises, etc.)
# Remember to adjust routes for TrainingCycle to match the (name, description) table from used_tables.txt,
# and remove/comment out routes that depended on the old member-specific TrainingCycle structure.
# Routes for preferences, weekly schedules, live sessions will follow a similar pattern of refactoring.