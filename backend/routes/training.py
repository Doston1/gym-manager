
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models.training import TrainingPlan
from backend.database.schemas.training import (
    TrainingPlanCreate,
    TrainingPlanResponse,
    TrainingPlanUpdate,
)
from typing import List
from ..database.crud import training as crud
from ..database.schemas.training import (
    TrainingPreferenceCreate, TrainingPreferenceUpdate, TrainingPreferenceResponse,
    WeeklyScheduleResponse, WeekPreferenceRequest, WeekPreferenceResponse,
    MemberScheduleAssignmentCreate, LiveTrainingSessionCreate, LiveTrainingSessionResponse,
    MemberProgressUpdate, MemberProgressResponse, TrainingCycleResponse,
    TrainingCycleSessionResponse, SessionExerciseResponse
)
import datetime
from ..auth import get_current_user

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


# Training Preferences Endpoints

@router.post("/preferences", response_model=TrainingPreferenceResponse)
async def create_training_preference(
    preference: TrainingPreferenceCreate,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new training preference for the current member."""
    # Check if user is a member
    if current_user["user_type"] != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can set training preferences"
        )
    
    # Check if today is a valid day for setting preferences
    if not crud.can_set_preferences_today(db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Preferences can only be set on Thursdays"
        )
    
    # Ensure member_id matches the current user's member_id
    member_id = current_user["member_id"]
    if preference.member_id != member_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only set preferences for yourself"
        )
    
    return crud.create_training_preference(
        db, 
        member_id=preference.member_id,
        day_of_week=preference.day_of_week,
        start_time=preference.start_time,
        end_time=preference.end_time,
        preference_type=preference.preference_type,
        trainer_id=preference.trainer_id,
        week_start_date=preference.week_start_date
    )

@router.get("/preferences/check", response_model=WeekPreferenceResponse)
async def check_preference_availability(
    request: WeekPreferenceRequest = None,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Check if today is a valid day for setting preferences and get existing preferences."""
    # Check if user is a member
    if current_user["user_type"] != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can view training preferences"
        )
    
    # Get member_id
    member_id = current_user["member_id"]
    
    # Determine if preferences can be set today
    can_set_preferences = crud.can_set_preferences_today(db)
    
    # Get the next week's start date
    week_start_date = request.week_start_date if request and request.week_start_date else crud.get_next_week_start_date()
    
    # Get existing preferences for this member for the next week
    preferences = crud.get_member_preferences_by_week(db, member_id, week_start_date)
    
    return {
        "can_set_preferences": can_set_preferences,
        "week_start_date": week_start_date,
        "preferences": preferences
    }

@router.put("/preferences/{preference_id}", response_model=TrainingPreferenceResponse)
async def update_training_preference(
    preference_id: int,
    preference: TrainingPreferenceUpdate,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing training preference."""
    # Check if user is a member
    if current_user["user_type"] != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can update training preferences"
        )
    
    # Check if today is a valid day for setting preferences
    if not crud.can_set_preferences_today(db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Preferences can only be updated on Thursdays"
        )
    
    # Get the preference to check ownership
    existing_preference = crud.get_training_preference(db, preference_id)
    if not existing_preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
    
    # Ensure the preference belongs to the current user
    if existing_preference.member_id != current_user["member_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own preferences"
        )
    
    return crud.update_training_preference(
        db,
        preference_id=preference_id,
        preference_type=preference.preference_type,
        trainer_id=preference.trainer_id
    )

@router.delete("/preferences/{preference_id}")
async def delete_training_preference(
    preference_id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a training preference."""
    # Check if user is a member
    if current_user["user_type"] != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can delete training preferences"
        )
    
    # Check if today is a valid day for setting preferences
    if not crud.can_set_preferences_today(db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Preferences can only be deleted on Thursdays"
        )
    
    # Get the preference to check ownership
    existing_preference = crud.get_training_preference(db, preference_id)
    if not existing_preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
    
    # Ensure the preference belongs to the current user
    if existing_preference.member_id != current_user["member_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own preferences"
        )
    
    success = crud.delete_training_preference(db, preference_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete preference"
        )
    
    return {"message": "Preference deleted successfully"}

# Weekly Schedule Endpoints

@router.get("/schedule/{week_start_date}", response_model=List[WeeklyScheduleResponse])
async def get_weekly_schedule(
    week_start_date: str,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get the weekly training schedule for a specific week."""
    # Convert string to date
    try:
        date_obj = datetime.datetime.strptime(week_start_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Get the schedule
    schedule = crud.get_weekly_schedules_by_week(db, date_obj)
    
    return schedule

@router.get("/schedule/member/{week_start_date}", response_model=List[WeeklyScheduleResponse])
async def get_member_weekly_schedule(
    week_start_date: str,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get the weekly training schedule for a specific member and week."""
    # Check if user is a member
    if current_user["user_type"] != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can view their schedules"
        )
    
    # Convert string to date
    try:
        date_obj = datetime.datetime.strptime(week_start_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Get the member's schedule
    member_id = current_user["member_id"]
    schedule = crud.get_member_schedule_by_week(db, member_id, date_obj)
    
    return schedule

@router.post("/schedule/generate/{week_start_date}")
async def generate_weekly_schedule(
    week_start_date: str,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate the weekly schedule for a specific week (manager only)."""
    # Check if user is a manager
    if current_user["user_type"] != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can generate schedules"
        )
    
    # Convert string to date
    try:
        date_obj = datetime.datetime.strptime(week_start_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Run the schedule generation
    success = crud.run_weekly_schedule_generation(db, date_obj)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Schedule generation failed"
        )
    
    return {"message": "Weekly schedule generated successfully"}

# Live Training Dashboard Endpoints

@router.post("/live/sessions", response_model=LiveTrainingSessionResponse)
async def create_live_session(
    session: LiveTrainingSessionCreate,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new live training session (trainer or manager only)."""
    # Check if user is a trainer or manager
    if current_user["user_type"] not in ["trainer", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers or managers can create live sessions"
        )
    
    # Create the live session
    live_session = crud.create_live_session(db, session.schedule_id)
    
    return live_session

@router.post("/live/sessions/{live_session_id}/start")
async def start_live_session(
    live_session_id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start a live training session (trainer or manager only)."""
    # Check if user is a trainer or manager
    if current_user["user_type"] not in ["trainer", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers or managers can start live sessions"
        )
    
    # Check if the session exists
    live_session = crud.get_live_session(db, live_session_id)
    if not live_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Live session not found"
        )
    
    # Start the live session
    updated_session = crud.start_live_session(db, live_session_id)
    
    return {"message": "Live session started"}

@router.post("/live/sessions/{live_session_id}/end")
async def end_live_session(
    live_session_id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """End a live training session (trainer or manager only)."""
    # Check if user is a trainer or manager
    if current_user["user_type"] not in ["trainer", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers or managers can end live sessions"
        )
    
    # Check if the session exists
    live_session = crud.get_live_session(db, live_session_id)
    if not live_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Live session not found"
        )
    
    # End the live session
    updated_session = crud.end_live_session(db, live_session_id)
    
    return {"message": "Live session ended"}

@router.get("/live/sessions/active", response_model=List[LiveTrainingSessionResponse])
async def get_active_live_sessions(
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all active (in progress) live training sessions (manager only)."""
    # Check if user is a manager
    if current_user["user_type"] != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can view all active sessions"
        )
    
    # Get active sessions
    sessions = crud.get_active_live_sessions(db)
    
    return sessions

@router.get("/live/sessions/member", response_model=List[LiveTrainingSessionResponse])
async def get_member_active_sessions(
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get active live training sessions for the current member."""
    # Check if user is a member
    if current_user["user_type"] != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can access their active sessions"
        )
    
    # Get active sessions for this member
    member_id = current_user["member_id"]
    sessions = crud.get_member_active_sessions(db, member_id)
    
    return sessions

@router.get("/live/sessions/trainer", response_model=List[LiveTrainingSessionResponse])
async def get_trainer_active_sessions(
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get active live training sessions for the current trainer."""
    # Check if user is a trainer
    if current_user["user_type"] != "trainer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers can access their active sessions"
        )
    
    # Get active sessions for this trainer
    trainer_id = current_user["trainer_id"]
    sessions = crud.get_trainer_active_sessions(db, trainer_id)
    
    return sessions

@router.get("/live/sessions/{live_session_id}/exercises", response_model=List[MemberProgressResponse])
async def get_member_session_exercises(
    live_session_id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get exercises for a member in a live training session."""
    # Check if user is a member
    if current_user["user_type"] != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can access their session exercises"
        )
    
    # Get member's exercises for this session
    member_id = current_user["member_id"]
    exercises = crud.get_member_session_exercises(db, live_session_id, member_id)
    
    return exercises

@router.post("/live/sessions/{live_session_id}/progress")
async def update_exercise_progress(
    live_session_id: int,
    exercise_id: int,
    progress: MemberProgressUpdate,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a member's exercise progress in a live session."""
    # Check if user is a member
    if current_user["user_type"] != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can update their exercise progress"
        )
    
    # Update the progress
    member_id = current_user["member_id"]
    success = crud.record_member_exercise_progress(
        db, 
        live_session_id=live_session_id,
        member_id=member_id,
        exercise_id=exercise_id,
        sets_completed=progress.sets_completed,
        actual_reps=progress.actual_reps,
        weight_used=progress.weight_used,
        comments=progress.comments
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update exercise progress"
        )
    
    return {"message": "Exercise progress updated"}

@router.post("/live/sessions/{live_session_id}/complete/{exercise_id}")
async def complete_exercise(
    live_session_id: int,
    exercise_id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark an exercise as completed for a member in a live session."""
    # Check if user is a member
    if current_user["user_type"] != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can complete their exercises"
        )
    
    # Complete the exercise
    member_id = current_user["member_id"]
    success = crud.complete_member_exercise(db, live_session_id, member_id, exercise_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete exercise"
        )
    
    return {"message": "Exercise marked as completed"}

# Training Cycle Endpoints

@router.get("/cycles", response_model=List[TrainingCycleResponse])
async def get_all_training_cycles(
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all available training cycles."""
    cycles = crud.get_all_training_cycles(db)
    return cycles

@router.get("/cycles/{cycle_id}/sessions", response_model=List[TrainingCycleSessionResponse])
async def get_cycle_sessions(
    cycle_id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all sessions for a training cycle."""
    sessions = crud.get_cycle_sessions(db, cycle_id)
    return sessions

@router.get("/cycles/sessions/{session_id}/exercises", response_model=List[SessionExerciseResponse])
async def get_session_exercises(
    session_id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all exercises for a training cycle session."""
    exercises = crud.get_session_exercises(db, session_id)
    return exercises

@router.post("/cycles/{cycle_id}/assign/{member_id}")
async def assign_cycle_to_member(
    cycle_id: int,
    member_id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assign a training cycle to a member (trainer only)."""
    # Check if user is a trainer
    if current_user["user_type"] != "trainer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers can assign training cycles"
        )
    
    # Assign the cycle
    success = crud.assign_cycle_to_member(db, member_id, cycle_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign training cycle"
        )
    
    return {"message": f"Training cycle {cycle_id} assigned to member {member_id}"}