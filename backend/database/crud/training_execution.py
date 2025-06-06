from typing import Optional
from backend.database.db_utils import get_sql, format_records, validate_payload
from mysql.connector import Error as MySQLError
from fastapi import HTTPException, status
import datetime # For current time if needed

# Import other CRUDs if FK validation is done explicitly (e.g. for member_id, plan_id)
# from backend.database.crud import user as crud_user
# from backend.database.crud import training_blueprints as crud_blueprints
# from backend.database.crud import scheduling as crud_scheduling


# --- MemberActivePlan Operations ---
def get_member_active_plan_by_id(db_conn, cursor, active_plan_id: int):
    sql = get_sql("member_active_plans_get_by_id")
    try:
        cursor.execute(sql, (active_plan_id,))
        record = format_records(cursor.fetchone())
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Active plan link ID {active_plan_id} not found.")
        return record
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_member_active_plans_by_member_id(db_conn, cursor, member_id: int, active_only: bool = False):
    # crud_user.get_member_by_id_pk(db_conn, cursor, member_id) # Validate member
    if active_only:
        sql = get_sql("member_active_plans_get_active_by_member_id")
    else:
        sql = get_sql("member_active_plans_get_by_member_id")
    try:
        cursor.execute(sql, (member_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def assign_plan_to_member(db_conn, cursor, assignment_data: dict):
    required_fields = ["member_id", "plan_id", "start_date"]
    optional_fields = ["end_date", "status"]
    try:
        validated_data = validate_payload(assignment_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault("status", "Active")
    # crud_user.get_member_by_id_pk(db_conn, cursor, validated_data['member_id'])
    # crud_blueprints.get_training_plan_by_id(db_conn, cursor, validated_data['plan_id'])

    # Prevent multiple 'Active' plans for the same member (as per UNIQUE constraint)
    if validated_data["status"] == "Active":
        active_plans = get_member_active_plans_by_member_id(db_conn, cursor, validated_data["member_id"], active_only=True)
        if active_plans:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member already has an active plan. Cancel or complete it first.")

    sql = get_sql("member_active_plans_create")
    try:
        cursor.execute(sql, validated_data)
        active_plan_id = cursor.lastrowid
        if not active_plan_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to assign plan to member.")
        return get_member_active_plan_by_id(db_conn, cursor, active_plan_id)
    except MySQLError as e:
        if e.errno == 1062: # Unique constraint
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflict assigning plan (e.g., already active or unique key violation).")
        if e.errno == 1452: # FK
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid member_id or plan_id.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_member_active_plan(db_conn, cursor, active_plan_id: int, update_data: dict):
    existing_assignment = get_member_active_plan_by_id(db_conn, cursor, active_plan_id) # Existence check
    optional_fields = ["start_date", "end_date", "status"] # member_id, plan_id usually not changed
    try:
        validated_data = validate_payload(update_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for update.")

    # Prevent multiple 'Active' plans if changing status to Active
    if validated_data.get("status") == "Active":
        active_plans = get_member_active_plans_by_member_id(db_conn, cursor, existing_assignment["member_id"], active_only=True)
        # Filter out the current plan being updated if it's already active and we are just changing other fields
        other_active_plans = [p for p in active_plans if p['active_plan_id'] != active_plan_id]
        if other_active_plans:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member already has another active plan.")

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("member_active_plans_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "active_plan_id": active_plan_id}

    try:
        cursor.execute(formatted_sql, update_params)
        return get_member_active_plan_by_id(db_conn, cursor, active_plan_id)
    except MySQLError as e:
        if e.errno == 1062 and 'status' in validated_data and validated_data['status'] == 'Active':
             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot have multiple active plans for a member.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")


# --- LiveSession Operations ---
def get_live_session_by_id(db_conn, cursor, live_session_id: int):
    sql = get_sql("live_sessions_get_by_id")
    try:
        cursor.execute(sql, (live_session_id,))
        session = format_records(cursor.fetchone())
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Live session ID {live_session_id} not found.")
        return session
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def start_live_session(db_conn, cursor, schedule_id: int, notes: Optional[str] = None):
    # crud_scheduling.get_weekly_schedule_by_id(db_conn, cursor, schedule_id) # Validate schedule_id

    # Check if there's already an active live session for this schedule_id
    active_sql = get_sql("live_sessions_get_by_schedule_id") # Modify or add a new one for active only
    cursor.execute(active_sql, (schedule_id,))
    existing_sessions = format_records(cursor.fetchall())
    for sess in existing_sessions:
        if sess['status'] in ['Started', 'In Progress']:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Schedule ID {schedule_id} already has an active live session (ID: {sess['live_session_id']}).")

    session_data = {
        "schedule_id": schedule_id,
        "start_time": datetime.datetime.now(), # Use current time
        "status": "Started",
        "notes": notes
    }
    sql = get_sql("live_sessions_create")
    try:
        cursor.execute(sql, session_data)
        live_session_id = cursor.lastrowid
        if not live_session_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to start live session.")
        return get_live_session_by_id(db_conn, cursor, live_session_id)
    except MySQLError as e:
        if e.errno == 1452:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid schedule_id.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_live_session_status(db_conn, cursor, live_session_id: int, new_status: str, notes: Optional[str] = None):
    live_session = get_live_session_by_id(db_conn, cursor, live_session_id) # Existence and fetch current notes

    valid_statuses = ['Started', 'In Progress', 'Completed', 'Cancelled']
    if new_status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {new_status}.")

    end_time = live_session['end_time'] # Preserve existing end_time unless completing/cancelling
    if new_status in ['Completed', 'Cancelled'] and not end_time:
        end_time = datetime.datetime.now()
    
    current_notes = live_session.get('notes', '')
    updated_notes = notes if notes is not None else current_notes # If new notes provided, use them, else keep old

    update_data = {
        "live_session_id": live_session_id,
        "status": new_status,
        "end_time": end_time,
        "notes": updated_notes
    }
    sql = get_sql("live_sessions_update_status_and_end_time") # Or a more generic update
    try:
        cursor.execute(sql, update_data)
        return get_live_session_by_id(db_conn, cursor, live_session_id)
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

# --- LiveSessionAttendance Operations ---
def member_check_in_live_session(db_conn, cursor, live_session_id: int, member_id: int, notes: Optional[str] = None):
    get_live_session_by_id(db_conn, cursor, live_session_id) # Validate live_session_id
    # crud_user.get_member_by_id_pk(db_conn, cursor, member_id) # Validate member_id

    # Check if member is already checked in
    existing_att_sql = get_sql("live_session_attendance_get_by_live_session_and_member")
    cursor.execute(existing_att_sql, {"live_session_id": live_session_id, "member_id": member_id})
    existing_attendance = cursor.fetchone()
    if existing_attendance and existing_attendance['status'] == 'Checked In':
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member already checked into this session.")
    if existing_attendance and existing_attendance['status'] == 'Checked Out': # Allow re-check-in? Or treat as new? For now, block.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member was previously checked out. Cannot re-check-in this record.")


    attendance_data = {
        "live_session_id": live_session_id,
        "member_id": member_id,
        "check_in_time": datetime.datetime.now(),
        "notes": notes
    }
    sql = get_sql("live_session_attendance_create_check_in")
    try:
        cursor.execute(sql, attendance_data)
        att_id = cursor.lastrowid
        if not att_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check in member.")
        return get_live_session_attendance_by_id(db_conn, cursor, att_id)
    except MySQLError as e:
        if e.errno == 1062: # Unique constraint (live_session_id, member_id)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Attendance record for this member and session already exists (possibly with different status).")
        if e.errno == 1452:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid live_session_id or member_id.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_live_session_attendance_status(db_conn, cursor, attendance_id: int, new_status: str, notes: Optional[str] = None):
    attendance_record = get_live_session_attendance_by_id(db_conn, cursor, attendance_id) # Existence check

    valid_statuses = ['Checked In', 'Checked Out', 'No Show']
    if new_status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid attendance status: {new_status}.")
    
    check_out_time = attendance_record['check_out_time']
    if new_status == 'Checked Out' and not check_out_time:
        check_out_time = datetime.datetime.now()
    elif new_status != 'Checked Out': # Clear checkout time if not checking out
        check_out_time = None
        
    current_notes = attendance_record.get('notes', '')
    updated_notes = notes if notes is not None else current_notes

    update_data = {
        "id": attendance_id,
        "status": new_status,
        "check_out_time": check_out_time,
        "notes": updated_notes
    }
    sql = get_sql("live_session_attendance_update_check_out_or_status")
    try:
        cursor.execute(sql, update_data)
        return get_live_session_attendance_by_id(db_conn, cursor, attendance_id)
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_live_session_attendance_by_id(db_conn, cursor, attendance_id: int):
    sql = get_sql("live_session_attendance_get_by_id")
    try:
        cursor.execute(sql, (attendance_id,))
        att = format_records(cursor.fetchone())
        if not att:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Attendance record ID {attendance_id} not found.")
        return att
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_attendance_for_live_session(db_conn, cursor, live_session_id: int):
    get_live_session_by_id(db_conn, cursor, live_session_id) # Validate
    sql = get_sql("live_session_attendance_get_by_live_session_id")
    try:
        cursor.execute(sql, (live_session_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")


# --- LoggedWorkouts & LoggedWorkoutExercises Operations ---
# This is where data from a completed LiveSession (or self-logging) is finalized.

def create_logged_workout(db_conn, cursor, workout_log_data: dict):
    required_fields = ["member_id", "workout_date"] # source can default
    optional_fields = ["member_active_plan_id", "training_plan_day_id", "duration_minutes_actual", "notes_overall_session", "source", "live_session_id"]
    try:
        validated_data = validate_payload(workout_log_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault("source", "self_logged")
    # Validate FKs if provided: member_id, member_active_plan_id, training_plan_day_id, live_session_id
    # crud_user.get_member_by_id_pk(...)
    # if validated_data.get('member_active_plan_id'): get_member_active_plan_by_id(...)
    # if validated_data.get('training_plan_day_id'): crud_blueprints.get_training_plan_day_by_id(...)
    # if validated_data.get('live_session_id'): get_live_session_by_id(...)

    sql = get_sql("logged_workouts_create")
    try:
        cursor.execute(sql, validated_data)
        logged_workout_id = cursor.lastrowid
        if not logged_workout_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create logged workout.")
        
        # If 'exercises' data is part of workout_log_data, create them in batch here
        exercises_to_log = workout_log_data.get("exercises", [])
        if exercises_to_log:
            create_logged_workout_exercises_batch(db_conn, cursor, logged_workout_id, exercises_to_log)

        return get_logged_workout_by_id(db_conn, cursor, logged_workout_id) # Fetch with details
    except MySQLError as e:
        if e.errno == 1452:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid FK in logged workout data.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_logged_workout_by_id(db_conn, cursor, logged_workout_id: int):
    sql = get_sql("logged_workouts_get_by_id") # This SQL should join for plan_title, day_name
    try:
        cursor.execute(sql, (logged_workout_id,))
        log = format_records(cursor.fetchone())
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Logged workout ID {logged_workout_id} not found.")
        # Fetch associated exercises
        log['exercises'] = get_logged_workout_exercises_by_workout_id(db_conn, cursor, logged_workout_id)
        return log
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_logged_workouts_by_member_id(db_conn, cursor, member_id: int):
    # crud_user.get_member_by_id_pk(db_conn, cursor, member_id) # Validate
    sql = get_sql("logged_workouts_get_by_member_id")
    try:
        cursor.execute(sql, (member_id,))
        workouts = format_records(cursor.fetchall())
        # Optionally, fetch exercises for each workout here if needed in a list view, or do it on demand
        return workouts
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def create_logged_workout_exercises_batch(db_conn, cursor, logged_workout_id: int, exercises_data: list):
    # This function assumes it's called within an existing transaction managed by create_logged_workout
    sql_single = get_sql("logged_workout_exercises_create_single")
    for exercise_log_data in exercises_data:
        required_fields = ["exercise_id", "order_in_workout"]
        optional_fields = [
            "training_day_exercise_id", "sets_prescribed", "reps_prescribed", "weight_prescribed",
            "rest_prescribed_seconds", "duration_prescribed_seconds", "sets_completed", "reps_actual_per_set",
            "weight_actual_per_set", "rest_actual_seconds_per_set", "duration_actual_seconds",
            "notes_exercise_specific", "completed_at"
        ]
        try:
            validated_data = validate_payload(exercise_log_data, required_fields, optional_fields)
        except ValueError as e:
            # Rollback should happen at higher level (create_logged_workout)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid exercise log data: {str(e)} for exercise order {exercise_log_data.get('order_in_workout')}")

        validated_data["logged_workout_id"] = logged_workout_id
        # crud_blueprints.get_exercise_by_id(db_conn, cursor, validated_data['exercise_id'])
        # if validated_data.get('training_day_exercise_id'):
        #     crud_blueprints.get_training_day_exercise_by_id(db_conn, cursor, validated_data['training_day_exercise_id'])
        try:
            cursor.execute(sql_single, validated_data)
            if cursor.lastrowid is None: # Or check affected_rows for executemany
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to log exercise (order: {validated_data.get('order_in_workout')}).")
        except MySQLError as e:
            if e.errno == 1452:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid FK for logged exercise (order: {validated_data.get('order_in_workout')}).")
            if e.errno == 1062: # Unique constraint on (logged_workout_id, order_in_workout)
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Duplicate order {validated_data.get('order_in_workout')} in logged workout.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error logging exercise: {str(e)}")
    return True # Indicates success for batch

def get_logged_workout_exercises_by_workout_id(db_conn, cursor, logged_workout_id: int):
    # get_logged_workout_by_id(db_conn, cursor, logged_workout_id) # Basic existence of parent, not needed if called internally
    sql = get_sql("logged_workout_exercises_get_by_logged_workout_id")
    try:
        cursor.execute(sql, (logged_workout_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

# ... (update/delete for logged_workouts and logged_workout_exercises can be added if needed)