from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.database.base import get_db_cursor, get_db_connection
from backend.database.crud import training_execution as crud_exec
from backend.database.crud import scheduling as crud_scheduling # For live session interaction
from backend.auth import get_current_user_data  # Import the auth function
from mysql.connector import Error as MySQLError
from typing import List, Optional, Dict, Any

from backend.database.db_utils import get_sql # For type hinting complex payloads

router = APIRouter(prefix="/training-execution", tags=["Training Execution & Logging"])

# Additional router for /training paths (to match frontend expectations)
training_router = APIRouter(prefix="/training", tags=["Training API"])

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

@router.get("/live-sessions/current")
def get_current_user_active_session_route(current_user: dict = Depends(get_current_user_data), db_conn_cursor = Depends(get_db_cursor)):
    """Get the current user's active live session"""
    db_conn, cursor = db_conn_cursor
    
    try:
        user_type = current_user.get("user_type")
        user_id = current_user.get("user_id")
        
        # Check for active live sessions based on user type
        if user_type == "member":
            member_id = current_user.get("member_id_pk")
            if not member_id:
                return {"active_session": None, "message": "Member ID not found"}
                
            # Query for active live sessions where this member is participating
            cursor.execute("""
                SELECT ls.*, ws.hall_id, h.name as hall_name, 
                       CONCAT(u.first_name, ' ', u.last_name) as trainer_name
                FROM live_sessions ls
                JOIN weekly_schedule ws ON ls.schedule_id = ws.schedule_id
                JOIN halls h ON ws.hall_id = h.hall_id
                JOIN trainers t ON ws.trainer_id = t.trainer_id
                JOIN users u ON t.user_id = u.user_id
                JOIN schedule_members sm ON ws.schedule_id = sm.schedule_id
                WHERE sm.member_id = %s 
                AND ls.status IN ('Active', 'In Progress')
                ORDER BY ls.start_time DESC
                LIMIT 1
            """, (member_id,))
            
        elif user_type == "trainer":
            trainer_id = current_user.get("trainer_id_pk")
            if not trainer_id:
                return {"active_session": None, "message": "Trainer ID not found"}
                
            # Query for active live sessions where this trainer is conducting
            cursor.execute("""
                SELECT ls.*, ws.hall_id, h.name as hall_name,
                       CONCAT(u.first_name, ' ', u.last_name) as trainer_name
                FROM live_sessions ls
                JOIN weekly_schedule ws ON ls.schedule_id = ws.schedule_id
                JOIN halls h ON ws.hall_id = h.hall_id
                JOIN trainers t ON ws.trainer_id = t.trainer_id
                JOIN users u ON t.user_id = u.user_id
                WHERE ws.trainer_id = %s 
                AND ls.status IN ('Active', 'In Progress')
                ORDER BY ls.start_time DESC
                LIMIT 1
            """, (trainer_id,))
            
        else:
            # Manager or other user types don't have "active sessions" in the same way
            return {"active_session": None, "message": "User type does not have active sessions"}
            
        active_session = cursor.fetchone()
        
        if active_session:
            return {"active_session": active_session, "message": "Active session found"}
        else:
            return {"active_session": None, "message": "No active session found"}
        
    except Exception as e:
        print(f"Error checking active session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error checking active session: {str(e)}")


# === Weekly Training Goals Routes ===
@router.post("/weekly-training-goals", status_code=status.HTTP_201_CREATED)
async def create_weekly_training_goal_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: member can only create their own goals, or trainer/manager can create for members
        new_goal = crud_exec.create_weekly_training_goal(db_conn, cursor, payload)
        db_conn.commit()
        return new_goal
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

@router.get("/weekly-training-goals/{goal_id}")
def get_weekly_training_goal_route(goal_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization: member can view their own goals, trainer/manager can view all
    return crud_exec.get_weekly_training_goal_by_id(db_conn, cursor, goal_id)

@router.get("/members/{member_id}/weekly-training-goals")
def get_member_weekly_training_goals_route(member_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization: member can view their own goals, trainer/manager can view all
    return crud_exec.get_weekly_training_goals_by_member_id(db_conn, cursor, member_id)

@router.get("/members/{member_id}/weekly-training-goals/{week_start_date}")
def get_member_weekly_training_goal_for_week_route(member_id: int, week_start_date: str, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization: member can view their own goals, trainer/manager can view all
    goal = crud_exec.get_weekly_training_goal_by_member_and_week(db_conn, cursor, member_id, week_start_date)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No weekly training goal found for member {member_id} and week {week_start_date}")
    return goal

@router.get("/weekly-training-goals/week/{week_start_date}")
def get_weekly_training_goals_for_week_route(week_start_date: str, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization: only trainer/manager can view all goals for a week
    return crud_exec.get_weekly_training_goals_by_week(db_conn, cursor, week_start_date)

@router.put("/weekly-training-goals/{goal_id}")
async def update_weekly_training_goal_route(goal_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: member can update their own goals, trainer/manager can update any
        updated_goal = crud_exec.update_weekly_training_goal(db_conn, cursor, goal_id, payload)
        db_conn.commit()
        return updated_goal
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

@router.delete("/weekly-training-goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weekly_training_goal_route(goal_id: int, db_conn = Depends(get_db_connection)):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: member can delete their own goals, trainer/manager can delete any
        crud_exec.delete_weekly_training_goal(db_conn, cursor, goal_id)
        db_conn.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
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

@router.post("/weekly-training-goals/upsert", status_code=status.HTTP_200_OK)
async def upsert_weekly_training_goal_route(request: Request, db_conn = Depends(get_db_connection)):
    """Insert or update a weekly training goal for a member and week"""
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: member can upsert their own goals, trainer/manager can upsert for any member
        goal = crud_exec.upsert_weekly_training_goal(db_conn, cursor, payload)
        db_conn.commit()
        return goal
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

# Also add routes to the training_router for /training paths
@training_router.post("/weekly-goals", status_code=status.HTTP_201_CREATED)
async def create_weekly_training_goal_training_route(request: Request, db_conn = Depends(get_db_connection)):
    return await create_weekly_training_goal_route(request, db_conn)

@training_router.get("/weekly-goals/{goal_id}")
def get_weekly_training_goal_training_route(goal_id: int, db_conn_cursor = Depends(get_db_cursor)):
    return get_weekly_training_goal_route(goal_id, db_conn_cursor)

@training_router.get("/members/{member_id}/weekly-goals")
def get_member_weekly_training_goals_training_route(member_id: int, db_conn_cursor = Depends(get_db_cursor)):
    return get_member_weekly_training_goals_route(member_id, db_conn_cursor)

@training_router.get("/members/{member_id}/weekly-goals/{week_start_date}")
def get_member_weekly_training_goal_for_week_training_route(member_id: int, week_start_date: str, db_conn_cursor = Depends(get_db_cursor)):
    return get_member_weekly_training_goal_for_week_route(member_id, week_start_date, db_conn_cursor)

@training_router.post("/weekly-goals/upsert", status_code=status.HTTP_200_OK)
async def upsert_weekly_training_goal_training_route(request: Request, db_conn = Depends(get_db_connection)):
    return await upsert_weekly_training_goal_route(request, db_conn)