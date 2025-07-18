from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.database.base import get_db_cursor, get_db_connection
from backend.database.crud import training_blueprints as crud_bp # Renamed for clarity
from backend.auth import get_current_user_data  # Import the auth function
from mysql.connector import Error as MySQLError
from typing import Optional

router = APIRouter(prefix="/training-blueprints", tags=["Training Blueprints"])

# Additional router for /training-plans paths (to match frontend expectations)
training_plans_router = APIRouter(prefix="/training-plans", tags=["Training Plans API"])

# === Exercise Routes ===
@router.post("/exercises", status_code=status.HTTP_201_CREATED)
async def create_exercise_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        new_exercise = crud_bp.create_exercise(db_conn, cursor, payload)
        db_conn.commit()
        return new_exercise
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@router.get("/exercises/{exercise_id}")
def get_exercise_route(exercise_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_exercise_by_id(db_conn, cursor, exercise_id)

@router.get("/exercises")
def get_all_exercises_route(is_active: bool = None, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_all_exercises(db_conn, cursor, is_active)

@router.put("/exercises/{exercise_id}")
async def update_exercise_route(exercise_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        updated_exercise = crud_bp.update_exercise(db_conn, cursor, exercise_id, payload)
        db_conn.commit()
        return updated_exercise
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_route(exercise_id: int, db_conn = Depends(get_db_connection)):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        crud_bp.delete_exercise(db_conn, cursor, exercise_id)
        db_conn.commit()
        return None
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()


# === TrainingPlan Routes ===
@router.post("/plans", status_code=status.HTTP_201_CREATED)
async def create_training_plan_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        new_plan = crud_bp.create_training_plan(db_conn, cursor, payload)
        db_conn.commit()
        return new_plan
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@router.get("/plans/{plan_id}")
def get_training_plan_route(plan_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_training_plan_by_id(db_conn, cursor, plan_id)

@router.get("/plans/{plan_id}/detailed")
def get_training_plan_detailed_route(plan_id: int, db_conn_cursor = Depends(get_db_cursor)):
    """Get a training plan with all its days and exercises"""
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_training_plan_detailed_by_id(db_conn, cursor, plan_id)

@router.get("/plans")
def get_all_training_plans_route(is_active: bool = None, trainer_id: int = None, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_all_training_plans(db_conn, cursor, is_active, trainer_id)

@router.put("/plans/{plan_id}")
async def update_training_plan_route(plan_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        updated_plan = crud_bp.update_training_plan(db_conn, cursor, plan_id, payload)
        db_conn.commit()
        return updated_plan
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_plan_route(plan_id: int, db_conn = Depends(get_db_connection)):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        crud_bp.delete_training_plan(db_conn, cursor, plan_id)
        db_conn.commit()
        return None
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

# === TrainingPlanDay Routes ===
@router.post("/plan-days", status_code=status.HTTP_201_CREATED)
async def create_training_plan_day_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        new_day = crud_bp.create_training_plan_day(db_conn, cursor, payload)
        db_conn.commit()
        return new_day
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@router.get("/plan-days/{day_id}")
def get_training_plan_day_route(day_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_training_plan_day_by_id(db_conn, cursor, day_id)

@router.get("/plans/{plan_id}/days")
def get_training_plan_days_for_plan_route(plan_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_training_plan_days_by_plan_id(db_conn, cursor, plan_id)

@router.put("/plan-days/{day_id}")
async def update_training_plan_day_route(day_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        updated_day = crud_bp.update_training_plan_day(db_conn, cursor, day_id, payload)
        db_conn.commit()
        return updated_day
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@router.delete("/plan-days/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_plan_day_route(day_id: int, db_conn = Depends(get_db_connection)):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        crud_bp.delete_training_plan_day(db_conn, cursor, day_id)
        db_conn.commit()
        return None
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()


# === TrainingDayExercise (linking exercise to plan day) Routes ===
@router.post("/day-exercises", status_code=status.HTTP_201_CREATED)
async def add_exercise_to_day_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        new_link = crud_bp.add_exercise_to_training_day(db_conn, cursor, payload)
        db_conn.commit()
        return new_link
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@router.get("/day-exercises/{tde_id}") # tde_id is the 'id' PK of training_day_exercises
def get_day_exercise_link_route(tde_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_training_day_exercise_by_id(db_conn, cursor, tde_id)

@router.get("/plan-days/{day_id}/exercises")
def get_exercises_for_plan_day_route(day_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_training_day_exercises_by_day_id(db_conn, cursor, day_id)

@router.put("/day-exercises/{tde_id}")
async def update_day_exercise_link_route(tde_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        updated_link = crud_bp.update_training_day_exercise(db_conn, cursor, tde_id, payload)
        db_conn.commit()
        return updated_link
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@router.delete("/day-exercises/{tde_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_exercise_from_day_route(tde_id: int, db_conn = Depends(get_db_connection)):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        crud_bp.remove_exercise_from_training_day(db_conn, cursor, tde_id)
        db_conn.commit()
        return None
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

# Route for frontend compatibility - maps /training-plans to the same functionality as /training-blueprints/plans
@training_plans_router.post("/custom", status_code=status.HTTP_201_CREATED)
async def create_custom_training_plan_route(request: Request, db_conn = Depends(get_db_connection)):
    """Create a custom training plan with full details (plan, days, exercises) and custom plan request"""
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        
        # Start transaction
        db_conn.start_transaction()
        
        # Extract main plan data
        plan_data = payload.get('plan', {})
        plan_data['is_custom'] = True  # Mark as custom
        plan_data['created_by'] = payload.get('user_id')  # Set creator
        
        # Create the training plan
        new_plan = crud_bp.create_training_plan(db_conn, cursor, plan_data)
        plan_id = new_plan['plan_id']
        
        # Create training plan days if provided
        days_data = payload.get('days', [])
        created_days = []
        
        for day_data in days_data:
            # Extract exercises data before adding to day_data
            exercises_data = day_data.pop('exercises', [])
            
            day_data['plan_id'] = plan_id
            new_day = crud_bp.create_training_plan_day(db_conn, cursor, day_data)
            day_id = new_day['day_id']
            
            # Create exercises for this day if provided
            created_exercises = []
            
            for exercise_data in exercises_data:
                exercise_data['day_id'] = day_id
                new_exercise = crud_bp.add_exercise_to_training_day(db_conn, cursor, exercise_data)
                created_exercises.append(new_exercise)
            
            new_day['exercises'] = created_exercises
            created_days.append(new_day)
        
        # Create custom plan request entry
        request_data = {
            'member_id': payload.get('member_id'),
            'goal': payload.get('goal', plan_data.get('description', 'Custom training plan request')),
            'days_per_week': plan_data.get('days_per_week'),
            'focus_areas': plan_data.get('primary_focus'),
            'equipment_available': plan_data.get('equipment_needed'),
            'health_limitations': payload.get('health_limitations'),
            'status': 'Completed',  # Since we're creating the plan immediately
            'completed_plan_id': plan_id,
            'notes': 'Custom plan created by member'
        }
        
        # Import custom plan request creation function
        from backend.database.crud import miscellaneous as crud_misc
        custom_request = crud_misc.create_custom_plan_request(db_conn, cursor, request_data)
        
        # Commit transaction
        db_conn.commit()
        
        # Return complete plan data
        complete_plan = {
            'plan': new_plan,
            'days': created_days,
            'custom_request': custom_request
        }
        
        return complete_plan
        
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@training_plans_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_training_plan_frontend_route(request: Request, db_conn = Depends(get_db_connection)):
    """Create a training plan - frontend compatible route"""
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        new_plan = crud_bp.create_training_plan(db_conn, cursor, payload)
        db_conn.commit()
        return new_plan
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@training_plans_router.get("/")
def get_all_training_plans_frontend_route(is_active: bool = None, trainer_id: int = None, db_conn_cursor = Depends(get_db_cursor)):
    """Get all training plans - frontend compatible route"""
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_all_training_plans(db_conn, cursor, is_active, trainer_id)

@training_plans_router.get("/exercises")
def get_all_exercises_frontend_route(is_active: Optional[bool] = None, db_conn_cursor = Depends(get_db_cursor)):
    """Get all exercises for frontend forms"""
    db_conn, cursor = db_conn_cursor
    # Default to True if not specified to get only active exercises
    if is_active is None:
        is_active = True
    return crud_bp.get_all_exercises(db_conn, cursor, is_active)

@training_plans_router.get("/{plan_id}")
def get_training_plan_frontend_route(plan_id: int, db_conn_cursor = Depends(get_db_cursor)):
    """Get a training plan - frontend compatible route"""
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_training_plan_by_id(db_conn, cursor, plan_id)

@training_plans_router.get("/{plan_id}/detailed")
def get_training_plan_detailed_frontend_route(plan_id: int, db_conn_cursor = Depends(get_db_cursor)):
    """Get a training plan with all its days and exercises - frontend compatible route"""
    db_conn, cursor = db_conn_cursor
    return crud_bp.get_training_plan_detailed_by_id(db_conn, cursor, plan_id)

@training_plans_router.get("/preferences/check")
def check_training_preferences(current_user: dict = Depends(get_current_user_data), db_conn_cursor = Depends(get_db_cursor)):
    """Check if training preferences can be set today and return current week info"""
    import datetime
    
    db_conn, cursor = db_conn_cursor
    
    try:
        # Only members can set training preferences
        if current_user.get("user_type") != "member":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only members can set training preferences")
        
        member_id = current_user.get("member_id_pk")
        if not member_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member ID not found")
        
        # Check if today is Thursday (preferences day)
        today = datetime.date.today()
        is_thursday = today.weekday() == 3  # Thursday is weekday 3
        
        # Calculate next week's start date (Sunday)
        days_until_sunday = (6 - today.weekday()) % 7
        if days_until_sunday == 0:  # If today is Sunday
            days_until_sunday = 7  # Get next Sunday
        
        next_week_start = today + datetime.timedelta(days=days_until_sunday)
        
        # Fetch existing preferences for the next week
        cursor.execute("""
            SELECT tp.*, CONCAT(u.first_name, ' ', u.last_name) as trainer_name
            FROM training_preferences tp
            LEFT JOIN trainers t ON tp.trainer_id = t.trainer_id
            LEFT JOIN users u ON t.user_id = u.user_id
            WHERE tp.member_id = %s 
            AND tp.week_start_date = %s
            ORDER BY tp.day_of_week, tp.start_time
        """, (member_id, next_week_start))
        
        existing_preferences = cursor.fetchall() or []
        
        return {
            "can_set_preferences": is_thursday,
            "week_start_date": next_week_start.isoformat(),
            "current_date": today.isoformat(),
            "is_thursday": is_thursday,
            "preferences": existing_preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error checking preferences: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error checking preferences: {str(e)}")

@training_plans_router.post("/public", status_code=status.HTTP_201_CREATED)
async def create_public_training_plan_route(request: Request, db_conn = Depends(get_db_connection)):
    """Create a public training plan with full details (plan, days, exercises)"""
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        
        # Start transaction
        db_conn.start_transaction()
        
        # Extract main plan data
        plan_data = payload.get('plan', {})
        plan_data['is_custom'] = False  # Mark as public
        
        # Create the training plan
        new_plan = crud_bp.create_training_plan(db_conn, cursor, plan_data)
        plan_id = new_plan['plan_id']
        
        # Create training plan days if provided
        days_data = payload.get('days', [])
        created_days = []
        
        for day_data in days_data:
            # Extract exercises data before adding to day_data
            exercises_data = day_data.pop('exercises', [])
            
            day_data['plan_id'] = plan_id
            new_day = crud_bp.create_training_plan_day(db_conn, cursor, day_data)
            day_id = new_day['day_id']
            
            # Create exercises for this day if provided
            created_exercises = []
            
            for exercise_data in exercises_data:
                exercise_data['day_id'] = day_id
                new_exercise = crud_bp.add_exercise_to_training_day(db_conn, cursor, exercise_data)
                created_exercises.append(new_exercise)
            
            new_day['exercises'] = created_exercises
            created_days.append(new_day)
        
        # Commit transaction
        db_conn.commit()
        
        # Return complete plan data
        complete_plan = {
            'plan': new_plan,
            'days': created_days
        }
        
        return complete_plan
        
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@training_plans_router.post("/exercises", status_code=status.HTTP_201_CREATED)
async def create_exercise_frontend_route(request: Request, db_conn = Depends(get_db_connection)):
    """Create an exercise - frontend compatible route"""
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        new_exercise = crud_bp.create_exercise(db_conn, cursor, payload)
        db_conn.commit()
        return new_exercise
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()