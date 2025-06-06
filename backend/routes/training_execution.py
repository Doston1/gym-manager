from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.database.base import get_db_cursor, get_db_connection
from backend.database.crud import training_execution as crud_exec
from backend.database.crud import scheduling as crud_scheduling # For live session interaction
from mysql.connector import Error as MySQLError
from typing import List, Optional, Dict, Any

from backend.database.db_utils import get_sql # For type hinting complex payloads

router = APIRouter(prefix="/training-execution", tags=["Training Execution & Logging"])

# === MemberActivePlan Routes ===
@router.post("/member-active-plans", status_code=status.HTTP_201_CREATED)
async def assign_plan_to_member_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: e.g., trainer assigns plan to member, or member self-assigns from public plans
        new_assignment = crud_exec.assign_plan_to_member(db_conn, cursor, payload)
        db_conn.commit()
        return new_assignment
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

@router.get("/member-active-plans/{active_plan_id}")
def get_member_active_plan_route(active_plan_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization
    return crud_exec.get_member_active_plan_by_id(db_conn, cursor, active_plan_id)

@router.get("/members/{member_id}/active-plans")
def get_member_plans_route(member_id: int, active_only: bool = False, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization
    return crud_exec.get_member_active_plans_by_member_id(db_conn, cursor, member_id, active_only)

@router.put("/member-active-plans/{active_plan_id}")
async def update_member_active_plan_route(active_plan_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization
        updated_assignment = crud_exec.update_member_active_plan(db_conn, cursor, active_plan_id, payload)
        db_conn.commit()
        return updated_assignment
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


# === LiveSession Routes ===
@router.post("/live-sessions/start", status_code=status.HTTP_201_CREATED)
async def start_live_session_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json() # Expected: {"schedule_id": int, "notes": "optional string"}
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: only trainer associated with schedule_id can start
        if "schedule_id" not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="schedule_id is required.")
        
        new_live_session = crud_exec.start_live_session(
            db_conn, cursor, payload["schedule_id"], payload.get("notes")
        )
        db_conn.commit()
        return new_live_session
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

@router.get("/live-sessions/{live_session_id}")
def get_live_session_route(live_session_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization
    return crud_exec.get_live_session_by_id(db_conn, cursor, live_session_id)

@router.put("/live-sessions/{live_session_id}/update-status")
async def update_live_session_status_route(live_session_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json() # Expected: {"status": "new_status", "notes": "optional"}
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization
        if "status" not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New status is required.")

        updated_session = crud_exec.update_live_session_status(
            db_conn, cursor, live_session_id, payload["status"], payload.get("notes")
        )
        
        # If session completed, log workout for attendees
        if updated_session['status'] == 'Completed':
            attendees = crud_exec.get_attendance_for_live_session(db_conn, cursor, live_session_id)
            for att in attendees:
                if att['status'] == 'Checked In' or att['status'] == 'Checked Out': # Only log for those who attended
                    # Find associated training_plan_day_id for this member for this schedule
                    schedule_member_info = None
                    try: # This logic might need refinement or its own CRUD helper
                        sm_sql = get_sql("schedule_members_get_by_schedule_id_and_member_id") # Needs: SELECT * FROM schedule_members WHERE schedule_id = %s AND member_id = %s
                        cursor.execute(sm_sql, (updated_session['schedule_id'], att['member_id']))
                        schedule_member_info = cursor.fetchone()
                    except MySQLError: # If query doesn't exist or fails
                        pass # Proceed without plan_day_id

                    workout_log_data = {
                        "member_id": att['member_id'],
                        "workout_date": updated_session['start_time'], # Or end_time
                        "duration_minutes_actual": (updated_session['end_time'] - updated_session['start_time']).total_seconds() / 60 if updated_session.get('end_time') else None,
                        "notes_overall_session": updated_session.get('notes'),
                        "source": "from_live_session",
                        "live_session_id": live_session_id,
                        "member_active_plan_id": None, # TODO: Determine this based on schedule_member_info or other logic
                        "training_plan_day_id": schedule_member_info.get('training_plan_day_id') if schedule_member_info else None,
                        "exercises": [] # TODO: Populate exercises performed during the live session
                                        # This part requires UI input during live session to capture exercise details
                    }
                    crud_exec.create_logged_workout(db_conn, cursor, workout_log_data)
        
        db_conn.commit()
        return updated_session
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

# === LiveSessionAttendance Routes ===
@router.post("/live-sessions/{live_session_id}/attendance/check-in", status_code=status.HTTP_201_CREATED)
async def member_check_in_route(live_session_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json() # Expected: {"member_id": int, "notes": "optional"}
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization
        if "member_id" not in payload:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="member_id is required.")
        
        check_in_record = crud_exec.member_check_in_live_session(
            db_conn, cursor, live_session_id, payload["member_id"], payload.get("notes")
        )
        db_conn.commit()
        return check_in_record
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

@router.put("/live-sessions/attendance/{attendance_id}/update-status")
async def update_attendance_status_route(attendance_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json() # Expected: {"status": "new_status", "notes": "optional"}
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization
        if "status" not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New status is required.")

        updated_attendance = crud_exec.update_live_session_attendance_status(
            db_conn, cursor, attendance_id, payload["status"], payload.get("notes")
        )
        db_conn.commit()
        return updated_attendance
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

@router.get("/live-sessions/{live_session_id}/attendance")
def get_live_session_attendance_route(live_session_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_exec.get_attendance_for_live_session(db_conn, cursor, live_session_id)


# === LoggedWorkout Routes ===
@router.post("/logged-workouts", status_code=status.HTTP_201_CREATED)
async def create_logged_workout_route(request: Request, db_conn = Depends(get_db_connection)):
    # Payload expected:
    # {
    #   "member_id": int, "workout_date": "YYYY-MM-DDTHH:MM:SS",
    #   "member_active_plan_id": int (optional), "training_plan_day_id": int (optional),
    #   "duration_minutes_actual": int (optional), "notes_overall_session": str (optional),
    #   "source": "self_logged" (optional, defaults), "live_session_id": int (optional),
    #   "exercises": [
    #     { "exercise_id": int, "order_in_workout": int, "training_day_exercise_id": int (opt),
    #       "sets_prescribed": int (opt), ... "reps_actual_per_set": "10,9,8" (opt), ... }, ...
    #   ]
    # }
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization (member logging for themselves, or trainer for member)
        new_log = crud_exec.create_logged_workout(db_conn, cursor, payload)
        db_conn.commit()
        return new_log # This will include exercises if they were logged
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

@router.get("/logged-workouts/{logged_workout_id}")
def get_logged_workout_route(logged_workout_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization
    return crud_exec.get_logged_workout_by_id(db_conn, cursor, logged_workout_id)

@router.get("/members/{member_id}/logged-workouts")
def get_member_logged_workouts_route(member_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization
    return crud_exec.get_logged_workouts_by_member_id(db_conn, cursor, member_id)

# Note: Update/Delete for logged_workouts and their exercises might be complex or less common.
# Typically, logs are immutable or have specific amendment processes.
# For simplicity, I'll omit PUT/DELETE for logged_workouts and logged_workout_exercises for now.
# If needed, they would follow similar patterns.