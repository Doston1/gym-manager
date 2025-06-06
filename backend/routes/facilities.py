from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.database.base import get_db_cursor, get_db_connection
from backend.database.crud import facilities as crud_facilities
from mysql.connector import Error as MySQLError
from typing import List, Optional # For query parameters

router = APIRouter(prefix="/facilities", tags=["Facilities Management"])

# === GymHours Routes ===
@router.post("/gym-hours", status_code=status.HTTP_201_CREATED)
async def create_gym_hour_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: only manager
        new_gym_hour = crud_facilities.create_gym_hour(db_conn, cursor, payload)
        db_conn.commit()
        return new_gym_hour
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e: # Catch specific DB errors
        if db_conn: db_conn.rollback()
        if e.errno == 1062: # Unique key violation (day_of_week)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@router.get("/gym-hours")
def get_all_gym_hours_route(db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_facilities.get_all_gym_hours(db_conn, cursor)

@router.get("/gym-hours/day/{day_of_week}")
def get_gym_hour_by_day_route(day_of_week: str, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    record = crud_facilities.get_gym_hour_by_day(db_conn, cursor, day_of_week)
    if not record: # CRUD returns None if not found by day
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gym hours for '{day_of_week}' not set.")
    return record

@router.put("/gym-hours/day/{day_of_week}") # Update by day is more intuitive for this
async def update_gym_hour_by_day_route(day_of_week: str, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: only manager
        updated_hour = crud_facilities.update_gym_hour_by_day(db_conn, cursor, day_of_week, payload)
        db_conn.commit()
        return updated_hour
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

# PUT by ID might be less common for gym_hours, but included for completeness if needed
@router.put("/gym-hours/id/{hours_id}")
async def update_gym_hour_by_id_route(hours_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        updated_hour = crud_facilities.update_gym_hour_by_id(db_conn, cursor, hours_id, payload)
        db_conn.commit()
        return updated_hour
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    # ... (similar error handling as above) ...
    finally:
        if cursor: cursor.close()


# DELETE for gym_hours is rare, usually records are updated.
# @router.delete("/gym-hours/{hours_id}", status_code=status.HTTP_204_NO_CONTENT) ...


# === Hall Routes ===
@router.post("/halls", status_code=status.HTTP_201_CREATED)
async def create_hall_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: only manager
        new_hall = crud_facilities.create_hall(db_conn, cursor, payload)
        db_conn.commit()
        return new_hall
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    # ... (similar error handling) ...
    finally:
        if cursor: cursor.close()

@router.get("/halls/{hall_id}")
def get_hall_route(hall_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_facilities.get_hall_by_id(db_conn, cursor, hall_id)

@router.get("/halls")
def get_all_halls_route(is_active: Optional[bool] = None, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_facilities.get_all_halls(db_conn, cursor, is_active)

@router.put("/halls/{hall_id}")
async def update_hall_route(hall_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: only manager
        updated_hall = crud_facilities.update_hall(db_conn, cursor, hall_id, payload)
        db_conn.commit()
        return updated_hall
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    # ... (similar error handling) ...
    finally:
        if cursor: cursor.close()

@router.delete("/halls/{hall_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hall_route(hall_id: int, db_conn = Depends(get_db_connection)):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: only manager
        crud_facilities.delete_hall(db_conn, cursor, hall_id)
        db_conn.commit()
        return None
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    # ... (similar error handling) ...
    finally:
        if cursor: cursor.close()