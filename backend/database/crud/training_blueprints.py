from backend.database.db_utils import get_sql, format_records, validate_payload
from mysql.connector import Error as MySQLError
from fastapi import HTTPException, status

# --- Exercise Operations ---
def get_exercise_by_id(db_conn, cursor, exercise_id: int):
    sql = get_sql("exercises_get_by_id")
    try:
        cursor.execute(sql, (exercise_id,))
        exercise = format_records(cursor.fetchone())
        if not exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise with ID {exercise_id} not found.")
        return exercise
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error fetching exercise: {str(e)}")

def get_all_exercises(db_conn, cursor, is_active: bool = None):
    params = ()
    if is_active is not None:
        sql = get_sql("exercises_get_all_by_active_status")
        params = (is_active,)
    else:
        sql = get_sql("exercises_get_all")
    try:
        cursor.execute(sql, params)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error fetching exercises: {str(e)}")

def create_exercise(db_conn, cursor, exercise_data: dict):
    required_fields = ["name", "primary_muscle_group"]
    optional_fields = ["description", "instructions", "difficulty_level", "secondary_muscle_groups", "equipment_needed", "image_url", "video_url", "is_active"]
    try:
        validated_data = validate_payload(exercise_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault("difficulty_level", "Beginner")
    validated_data.setdefault("is_active", True)

    sql = get_sql("exercises_create")
    try:
        cursor.execute(sql, validated_data)
        exercise_id = cursor.lastrowid
        if not exercise_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create exercise.")
        return get_exercise_by_id(db_conn, cursor, exercise_id)
    except MySQLError as e:
        if e.errno == 1062: # Assuming name is unique in DB
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Exercise name '{validated_data.get('name')}' already exists.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error creating exercise: {str(e)}")

def update_exercise(db_conn, cursor, exercise_id: int, exercise_data: dict):
    get_exercise_by_id(db_conn, cursor, exercise_id) # Existence check
    optional_fields = ["name", "description", "instructions", "difficulty_level", "primary_muscle_group", "secondary_muscle_groups", "equipment_needed", "image_url", "video_url", "is_active"]
    try:
        validated_data = validate_payload(exercise_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for update.")

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("exercises_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "exercise_id": exercise_id}

    try:
        cursor.execute(formatted_sql, update_params)
        return get_exercise_by_id(db_conn, cursor, exercise_id)
    except MySQLError as e:
        if e.errno == 1062 and 'name' in validated_data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Exercise name '{validated_data.get('name')}' already exists.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error updating exercise: {str(e)}")

def delete_exercise(db_conn, cursor, exercise_id: int):
    get_exercise_by_id(db_conn, cursor, exercise_id) # Existence check
    sql = get_sql("exercises_delete_by_id")
    try:
        cursor.execute(sql, (exercise_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise ID {exercise_id} not found for deletion.")
        return True
    except MySQLError as e:
        if e.errno == 1451: # FK constraint from training_day_exercises
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete exercise ID {exercise_id}: it's used in training plans.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error deleting exercise: {str(e)}")

# --- TrainingPlan Operations ---
def get_training_plan_by_id(db_conn, cursor, plan_id: int):
    sql = get_sql("training_plans_get_by_id")
    try:
        cursor.execute(sql, (plan_id,))
        plan = format_records(cursor.fetchone())
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Training plan ID {plan_id} not found.")
        return plan
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_training_plan_detailed_by_id(db_conn, cursor, plan_id: int):
    """Get a training plan with all its days and exercises"""
    sql = get_sql("training_plans_get_detailed_by_id")
    try:
        cursor.execute(sql, (plan_id,))
        rows = format_records(cursor.fetchall())
        
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Training plan ID {plan_id} not found.")
        
        # Structure the data
        plan = {
            'plan_id': rows[0]['plan_id'],
            'title': rows[0]['title'],
            'description': rows[0]['description'],
            'difficulty_level': rows[0]['difficulty_level'],
            'duration_weeks': rows[0]['duration_weeks'],
            'days_per_week': rows[0]['days_per_week'],
            'primary_focus': rows[0]['primary_focus'],
            'secondary_focus': rows[0]['secondary_focus'],
            'target_gender': rows[0]['target_gender'],
            'min_age': rows[0]['min_age'],
            'max_age': rows[0]['max_age'],
            'equipment_needed': rows[0]['equipment_needed'],
            'created_by': rows[0]['created_by'],
            'is_custom': rows[0]['is_custom'],
            'is_active': rows[0]['is_active'],
            'created_at': rows[0]['created_at'],
            'updated_at': rows[0]['updated_at'],
            'days': []
        }
        
        # Group by days
        days_dict = {}
        for row in rows:
            if row['day_id']:  # Only if there are days
                day_id = row['day_id']
                if day_id not in days_dict:
                    days_dict[day_id] = {
                        'day_id': day_id,
                        'day_number': row['day_number'],
                        'name': row['day_name'],
                        'focus': row['day_focus'],
                        'description': row['day_description'],
                        'duration_minutes': row['duration_minutes'],
                        'calories_burn_estimate': row['calories_burn_estimate'],
                        'exercises': []
                    }
                
                # Add exercise if it exists
                if row['exercise_id']:
                    exercise = {
                        'exercise_link_id': row['exercise_link_id'],
                        'exercise_id': row['exercise_id'],
                        'order': row['exercise_order'],
                        'sets': row['sets'],
                        'reps': row['reps'],
                        'rest_seconds': row['rest_seconds'],
                        'duration_seconds': row['duration_seconds'],
                        'notes': row['exercise_notes'],
                        'exercise_name': row['exercise_name'],
                        'exercise_description': row['exercise_description'],
                        'exercise_instructions': row['exercise_instructions'],
                        'exercise_difficulty': row['exercise_difficulty'],
                        'primary_muscle_group': row['primary_muscle_group'],
                        'secondary_muscle_groups': row['secondary_muscle_groups'],
                        'exercise_equipment': row['exercise_equipment'],
                        'image_url': row['image_url'],
                        'video_url': row['video_url']
                    }
                    days_dict[day_id]['exercises'].append(exercise)
        
        # Convert to list and sort by day number
        plan['days'] = sorted(days_dict.values(), key=lambda x: x['day_number'])
        
        return plan
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_all_training_plans(db_conn, cursor, is_active: bool = None, trainer_id: int = None):
    params = []
    base_sql = "SELECT plan_id, title, description, difficulty_level, duration_weeks, days_per_week, primary_focus, secondary_focus, target_gender, min_age, max_age, equipment_needed, created_by, is_custom, is_active, created_at, updated_at FROM training_plans"
    conditions = []
    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)
    if trainer_id is not None:
        conditions.append("created_by = %s")
        params.append(trainer_id)
    
    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)
    base_sql += " ORDER BY title;"

    try:
        cursor.execute(base_sql, tuple(params))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")


def create_training_plan(db_conn, cursor, plan_data: dict):
    required_fields = ["title", "duration_weeks", "days_per_week", "primary_focus"]
    optional_fields = ["description", "difficulty_level", "secondary_focus", "target_gender", "min_age", "max_age", "equipment_needed", "created_by", "is_custom", "is_active"]
    try:
        validated_data = validate_payload(plan_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault("difficulty_level", "All Levels")
    validated_data.setdefault("target_gender", "Any")
    validated_data.setdefault("is_custom", False)
    validated_data.setdefault("is_active", True)

    sql = get_sql("training_plans_create")
    try:
        cursor.execute(sql, validated_data)
        plan_id = cursor.lastrowid
        if not plan_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create training plan.")
        return get_training_plan_by_id(db_conn, cursor, plan_id)
    except MySQLError as e:
        if e.errno == 1452 and 'created_by' in validated_data and validated_data['created_by'] is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid trainer ID for 'created_by'.")
        if e.errno == 1062 and 'title' in validated_data: # If title is unique
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Training plan title '{validated_data.get('title')}' already exists.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_training_plan(db_conn, cursor, plan_id: int, plan_data: dict):
    get_training_plan_by_id(db_conn, cursor, plan_id) # Existence check
    optional_fields = ["title", "description", "difficulty_level", "duration_weeks", "days_per_week", "primary_focus", "secondary_focus", "target_gender", "min_age", "max_age", "equipment_needed", "created_by", "is_custom", "is_active"]
    try:
        validated_data = validate_payload(plan_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for update.")

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("training_plans_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "plan_id": plan_id}

    try:
        cursor.execute(formatted_sql, update_params)
        return get_training_plan_by_id(db_conn, cursor, plan_id)
    except MySQLError as e:
        if e.errno == 1452 and 'created_by' in validated_data and validated_data['created_by'] is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid trainer ID for 'created_by'.")
        if e.errno == 1062 and 'title' in validated_data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Training plan title '{validated_data.get('title')}' already exists.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def delete_training_plan(db_conn, cursor, plan_id: int):
    get_training_plan_by_id(db_conn, cursor, plan_id) # Existence check
    # Before deleting a plan, ensure all its days (and their exercises) are deleted if CASCADE is not set up, or handle it.
    # Assuming ON DELETE CASCADE from training_plans to training_plan_days.
    # And from training_plan_days to training_day_exercises.
    sql = get_sql("training_plans_delete_by_id")
    try:
        cursor.execute(sql, (plan_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Training plan ID {plan_id} not found for deletion.")
        return True
    except MySQLError as e:
        if e.errno == 1451: # FK constraint from member_saved_plans or member_active_plans or custom_plan_requests
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete plan ID {plan_id}: it's referenced by member records or custom requests.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")


# --- TrainingPlanDay Operations ---
def get_training_plan_day_by_id(db_conn, cursor, day_id: int):
    sql = get_sql("training_plan_days_get_by_id")
    try:
        cursor.execute(sql, (day_id,))
        day = format_records(cursor.fetchone())
        if not day:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Training plan day ID {day_id} not found.")
        return day
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_training_plan_days_by_plan_id(db_conn, cursor, plan_id: int):
    get_training_plan_by_id(db_conn, cursor, plan_id) # Ensure parent plan exists
    sql = get_sql("training_plan_days_get_by_plan_id")
    try:
        cursor.execute(sql, (plan_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def create_training_plan_day(db_conn, cursor, day_data: dict):
    required_fields = ["plan_id", "day_number"]
    optional_fields = ["name", "focus", "description", "duration_minutes", "calories_burn_estimate"]
    try:
        validated_data = validate_payload(day_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    get_training_plan_by_id(db_conn, cursor, validated_data['plan_id']) # Ensure parent plan exists

    sql = get_sql("training_plan_days_create")
    try:
        cursor.execute(sql, validated_data)
        day_id = cursor.lastrowid
        if not day_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create training plan day.")
        return get_training_plan_day_by_id(db_conn, cursor, day_id)
    except MySQLError as e:
        if e.errno == 1452: # FK for plan_id
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 'plan_id'.")
        if e.errno == 1062: # UNIQUE (plan_id, day_number)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Day number {validated_data.get('day_number')} already exists for plan ID {validated_data.get('plan_id')}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_training_plan_day(db_conn, cursor, day_id: int, day_data: dict):
    get_training_plan_day_by_id(db_conn, cursor, day_id) # Existence check
    # plan_id cannot be changed here easily due to unique constraint (plan_id, day_number)
    # if plan_id needs to change, it's better to delete and recreate the day for a different plan.
    optional_fields = ["day_number", "name", "focus", "description", "duration_minutes", "calories_burn_estimate"]
    try:
        validated_data = validate_payload(day_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for update.")

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("training_plan_days_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "day_id": day_id}

    try:
        cursor.execute(formatted_sql, update_params)
        return get_training_plan_day_by_id(db_conn, cursor, day_id)
    except MySQLError as e:
        if e.errno == 1062 and 'day_number' in validated_data: # Check unique for day_number within its current plan
            # This check is tricky without knowing the original plan_id if it's not being updated.
            # The DB constraint should catch this.
            current_day = get_training_plan_day_by_id(db_conn, cursor, day_id) # Re-fetch to be sure
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Day number {validated_data.get('day_number')} already exists for plan ID {current_day['plan_id']}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def delete_training_plan_day(db_conn, cursor, day_id: int):
    get_training_plan_day_by_id(db_conn, cursor, day_id) # Existence check
    # Assuming ON DELETE CASCADE from training_plan_days to training_day_exercises
    sql = get_sql("training_plan_days_delete_by_id")
    try:
        cursor.execute(sql, (day_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Training plan day ID {day_id} not found for deletion.")
        return True
    except MySQLError as e:
        if e.errno == 1451: # Should be handled by CASCADE if set up for training_day_exercises.
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete plan day ID {day_id}: it has exercises linked (setup ON DELETE CASCADE or delete exercises first).")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")


# --- TrainingDayExercise Operations ---
def get_training_day_exercise_by_id(db_conn, cursor, tde_id: int):
    sql = get_sql("training_day_exercises_get_by_id")
    try:
        cursor.execute(sql, (tde_id,))
        record = format_records(cursor.fetchone())
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Training day exercise link ID {tde_id} not found.")
        return record
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_training_day_exercises_by_day_id(db_conn, cursor, day_id: int):
    get_training_plan_day_by_id(db_conn, cursor, day_id) # Ensure parent day exists
    sql = get_sql("training_day_exercises_get_by_day_id")
    try:
        cursor.execute(sql, (day_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def add_exercise_to_training_day(db_conn, cursor, tde_data: dict):
    required_fields = ["day_id", "exercise_id", "order"]
    optional_fields = ["sets", "reps", "rest_seconds", "duration_seconds", "notes"]
    try:
        validated_data = validate_payload(tde_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    get_training_plan_day_by_id(db_conn, cursor, validated_data['day_id'])
    get_exercise_by_id(db_conn, cursor, validated_data['exercise_id'])

    sql = get_sql("training_day_exercises_create")
    try:
        cursor.execute(sql, validated_data)
        tde_id = cursor.lastrowid
        if not tde_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add exercise to day.")
        return get_training_day_exercise_by_id(db_conn, cursor, tde_id)
    except MySQLError as e:
        if e.errno == 1452:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 'day_id' or 'exercise_id'.")
        # Consider UNIQUE constraint on (day_id, order) if needed
        # if e.errno == 1062:
        #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Order {validated_data.get('order')} already exists for day ID {validated_data.get('day_id')}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_training_day_exercise(db_conn, cursor, tde_id: int, tde_data: dict):
    get_training_day_exercise_by_id(db_conn, cursor, tde_id) # Existence check
    optional_fields = ["day_id", "exercise_id", "order", "sets", "reps", "rest_seconds", "duration_seconds", "notes"]
    try:
        validated_data = validate_payload(tde_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for update.")

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    # `order` is a keyword, ensure it's backticked in SQL if not in placeholder
    # If placeholder is `order`, and SQL column is `order`, it's fine.
    # If SQL column is `order` (keyword), it should be `order` = %(order)s
    sql_template = get_sql("training_day_exercises_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "id": tde_id} # SQL uses 'id' for its PK

    try:
        cursor.execute(formatted_sql, update_params)
        return get_training_day_exercise_by_id(db_conn, cursor, tde_id)
    except MySQLError as e:
        if e.errno == 1452 and ('day_id' in validated_data or 'exercise_id' in validated_data):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 'day_id' or 'exercise_id' on update.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def remove_exercise_from_training_day(db_conn, cursor, tde_id: int):
    get_training_day_exercise_by_id(db_conn, cursor, tde_id) # Existence check
    sql = get_sql("training_day_exercises_delete_by_id")
    try:
        cursor.execute(sql, (tde_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Training day exercise link ID {tde_id} not found.")
        return True
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")