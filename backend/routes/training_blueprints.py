from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.database.base import get_db_cursor, get_db_connection
from backend.database.crud import training_blueprints as crud_bp # Renamed for clarity
from mysql.connector import Error as MySQLError

router = APIRouter(prefix="/training-blueprints", tags=["Training Blueprints"])

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