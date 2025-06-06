from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.database.base import get_db_cursor, get_db_connection
from backend.database.crud import scheduling as crud_scheduling
from mysql.connector import Error as MySQLError
from typing import List, Optional # For query parameters

router = APIRouter(prefix="/scheduling", tags=["Scheduling"])

# === TrainingPreference Routes ===
@router.post("/preferences", status_code=status.HTTP_201_CREATED)
async def create_training_preference_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add logic to get member_id from authenticated user (e.g., current_user['member_id_pk'])
        # For now, assuming member_id is in payload
        # if 'member_id' not in payload and current_user: payload['member_id'] = current_user['member_id_pk']
        new_pref = crud_scheduling.create_training_preference(db_conn, cursor, payload)
        db_conn.commit()
        return new_pref
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

@router.get("/preferences/{preference_id}")
def get_training_preference_route(preference_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_scheduling.get_training_preference_by_id(db_conn, cursor, preference_id)

@router.get("/members/{member_id}/preferences-for-week")
def get_member_preferences_for_week_route(member_id: int, week_start_date: str, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization: ensure current user can view this member's preferences
    return crud_scheduling.get_training_preferences_by_member_and_week(db_conn, cursor, member_id, week_start_date)

@router.put("/preferences/{preference_id}")
async def update_training_preference_route(preference_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: ensure current user owns this preference
        updated_pref = crud_scheduling.update_training_preference(db_conn, cursor, preference_id, payload)
        db_conn.commit()
        return updated_pref
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

@router.delete("/preferences/{preference_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_preference_route(preference_id: int, db_conn = Depends(get_db_connection)):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: ensure current user owns this preference
        crud_scheduling.delete_training_preference(db_conn, cursor, preference_id)
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


# === WeeklySchedule Routes ===
@router.post("/weekly-schedules", status_code=status.HTTP_201_CREATED)
async def create_weekly_schedule_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: only manager/trainer can create
        # Add logic to get created_by from authenticated user
        # if 'created_by' not in payload and current_user: payload['created_by'] = current_user['user_id_pk']
        new_schedule = crud_scheduling.create_weekly_schedule(db_conn, cursor, payload)
        db_conn.commit()
        return new_schedule
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

@router.get("/weekly-schedules/{schedule_id}")
def get_weekly_schedule_route(schedule_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Consider returning a more detailed view here if needed (e.g., with member count)
    return crud_scheduling.get_weekly_schedule_by_id(db_conn, cursor, schedule_id)

@router.get("/weekly-schedules-for-week/{week_start_date}")
def get_schedules_for_week_route(
    week_start_date: str, 
    trainer_id: Optional[int] = None, 
    hall_id: Optional[int] = None, 
    db_conn_cursor = Depends(get_db_cursor)
):
    db_conn, cursor = db_conn_cursor
    return crud_scheduling.get_weekly_schedules_by_week(db_conn, cursor, week_start_date, trainer_id, hall_id)

@router.put("/weekly-schedules/{schedule_id}")
async def update_weekly_schedule_route(schedule_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: only manager/trainer or creator can update
        updated_schedule = crud_scheduling.update_weekly_schedule(db_conn, cursor, schedule_id, payload)
        db_conn.commit()
        return updated_schedule
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

@router.delete("/weekly-schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weekly_schedule_route(schedule_id: int, db_conn = Depends(get_db_connection)):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization
        crud_scheduling.delete_weekly_schedule(db_conn, cursor, schedule_id)
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


# === ScheduleMembers Routes (Booking a member into a weekly_schedule slot) ===
@router.post("/schedule-members", status_code=status.HTTP_201_CREATED)
async def add_member_to_schedule_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization (e.g., member booking themselves, or trainer/manager booking for member)
        new_booking = crud_scheduling.add_member_to_schedule(db_conn, cursor, payload)
        db_conn.commit()
        return new_booking
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

@router.get("/schedule-members/{sm_id}") # sm_id is schedule_members.id
def get_schedule_member_link_route(sm_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_scheduling.get_schedule_member_by_id(db_conn, cursor, sm_id)

@router.get("/weekly-schedules/{schedule_id}/members")
def get_members_for_schedule_route(schedule_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_scheduling.get_schedule_members_by_schedule_id(db_conn, cursor, schedule_id)

@router.get("/members/{member_id}/scheduled-for-week/{week_start_date}")
def get_member_schedule_for_week_route(member_id: int, week_start_date: str, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization: member can see their own, trainer/manager can see others
    return crud_scheduling.get_schedule_members_by_member_id_and_week(db_conn, cursor, member_id, week_start_date)


@router.put("/schedule-members/{sm_id}")
async def update_schedule_member_route(sm_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization
        updated_booking = crud_scheduling.update_schedule_member(db_conn, cursor, sm_id, payload)
        db_conn.commit()
        return updated_booking
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

@router.delete("/schedule-members/{sm_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member_from_schedule_route(sm_id: int, db_conn = Depends(get_db_connection)):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization
        crud_scheduling.remove_member_from_schedule(db_conn, cursor, sm_id)
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