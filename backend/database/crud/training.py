# In backend/database/crud/training.py

from backend.database.db_utils import get_sql, format_records, validate_payload
from mysql.connector import Error as DBError
from fastapi import HTTPException
import datetime # For type hinting if needed, and default values

# --- TrainingPlan Operations ---
def get_training_plan_by_id(db_conn, cursor, plan_id: int):
    sql = get_sql("training_plans_get_by_id")
    cursor.execute(sql, (plan_id,))
    return format_records(cursor.fetchone())

def get_all_training_plans(db_conn, cursor):
    sql = get_sql("training_plans_get_all")
    cursor.execute(sql)
    return format_records(cursor.fetchall())

def create_training_plan(db_conn, cursor, plan_data: dict):
    required_fields = ["title", "duration_weeks", "days_per_week", "primary_focus"]
    optional_fields = [
        "description", "difficulty_level", "secondary_focus", "target_gender",
        "min_age", "max_age", "equipment_needed", "created_by", "is_custom", "is_active"
    ]
    try:
        validated_data = validate_payload(plan_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Set defaults
    validated_data.setdefault("difficulty_level", "All Levels")
    validated_data.setdefault("target_gender", "Any")
    validated_data.setdefault("is_custom", False)
    validated_data.setdefault("is_active", True)

    sql = get_sql("training_plans_create")
    try:
        cursor.execute(sql, validated_data)
        db_conn.commit()
        plan_id = cursor.lastrowid
        return get_training_plan_by_id(db_conn, cursor, plan_id)
    except DBError as e:
        db_conn.rollback()
        # Check for foreign key constraint violation if created_by is invalid
        if e.errno == 1452: # Cannot add or update a child row: a foreign key constraint fails
            raise HTTPException(status_code=400, detail=f"Invalid 'created_by' (trainer_id): Trainer does not exist.")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def update_training_plan(db_conn, cursor, plan_id: int, plan_data: dict):
    existing_plan = get_training_plan_by_id(db_conn, cursor, plan_id)
    if not existing_plan:
        return None

    optional_fields = [
        "title", "description", "difficulty_level", "duration_weeks", "days_per_week",
        "primary_focus", "secondary_focus", "target_gender", "min_age", "max_age",
        "equipment_needed", "created_by", "is_custom", "is_active"
    ]
    try:
        validated_data = validate_payload(plan_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not validated_data:
        raise HTTPException(status_code=400, detail="No data provided for update.")

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("training_plans_update_by_id")
    sql = sql_template.replace("{set_clauses}", set_clauses)
    
    update_params = {**validated_data, "plan_id": plan_id}

    try:
        cursor.execute(sql, update_params)
        db_conn.commit()
        return get_training_plan_by_id(db_conn, cursor, plan_id)
    except DBError as e:
        db_conn.rollback()
        if e.errno == 1452 and 'created_by' in validated_data:
             raise HTTPException(status_code=400, detail=f"Invalid 'created_by' (trainer_id): Trainer does not exist.")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def delete_training_plan(db_conn, cursor, plan_id: int):
    existing_plan = get_training_plan_by_id(db_conn, cursor, plan_id)
    if not existing_plan:
        return False
    sql = get_sql("training_plans_delete_by_id")
    try:
        cursor.execute(sql, (plan_id,))
        db_conn.commit()
        return cursor.rowcount > 0
    except DBError as e:
        db_conn.rollback()
        # Handle potential FK issues if plans are linked elsewhere and not ON DELETE CASCADE
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# ... Implement similar CRUD for TrainingPlanDay, Exercise, TrainingDayExercise,
# MemberSavedPlan, CustomPlanRequest, TrainingPreference, WeeklySchedule,
# ScheduleMember, LiveSession, LiveSessionExercise, LiveSessionAttendance etc.
# And the NEW training_cycles (name, description), training_cycle_sessions, session_exercises.