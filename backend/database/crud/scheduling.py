from typing import Dict, List
from backend.database.db_utils import get_sql, format_records, validate_payload
from mysql.connector import Error as MySQLError
from fastapi import HTTPException, status
from backend.database.crud import training_blueprints as crud_blueprints # For validating training_plan_day_id
# from backend.database.crud import user as crud_user # For validating member_id, trainer_id if needed explicitly

# --- TrainingPreference Operations ---
def get_training_preference_by_id(db_conn, cursor, preference_id: int):
    sql = get_sql("training_preferences_get_by_id")
    try:
        cursor.execute(sql, (preference_id,))
        pref = format_records(cursor.fetchone())
        if not pref:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Training preference ID {preference_id} not found.")
        return pref
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_training_preferences_by_member_and_week(db_conn, cursor, member_id: int, week_start_date: str):
    # crud_user.get_member_by_id_pk(db_conn, cursor, member_id) # Validate member_id
    sql = get_sql("training_preferences_get_by_member_and_week")
    try:
        cursor.execute(sql, {"member_id": member_id, "week_start_date": week_start_date})
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def create_training_preference(db_conn, cursor, preference_data: dict):
    required_fields = ["member_id", "week_start_date", "day_of_week", "start_time", "end_time", "preference_type"]
    optional_fields = ["trainer_id"]
    try:
        validated_data = validate_payload(preference_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    # crud_user.get_member_by_id_pk(db_conn, cursor, validated_data['member_id']) # Validate member_id
    # if validated_data.get('trainer_id'):
    #     crud_user.get_trainer_by_id_pk(db_conn, cursor, validated_data['trainer_id']) # Validate trainer_id

    sql = get_sql("training_preferences_create")
    try:
        cursor.execute(sql, validated_data)
        pref_id = cursor.lastrowid
        if not pref_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create preference.")
        return get_training_preference_by_id(db_conn, cursor, pref_id)
    except MySQLError as e:
        if e.errno == 1062: # Unique constraint violation
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This preference slot already exists for the member and week.")
        if e.errno == 1452: # FK violation
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid member_id or trainer_id.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_training_preference(db_conn, cursor, preference_id: int, preference_data: dict):
    get_training_preference_by_id(db_conn, cursor, preference_id) # Existence check
    # Note: Updating day/time/week is complex due to UNIQUE constraint; usually means delete & recreate.
    # This update typically for preference_type or trainer_id.
    optional_fields = ["preference_type", "trainer_id", "start_time", "end_time", "day_of_week", "week_start_date"] # Allow more if needed
    try:
        validated_data = validate_payload(preference_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for update.")

    # if validated_data.get('trainer_id'):
    #     crud_user.get_trainer_by_id_pk(db_conn, cursor, validated_data['trainer_id']) # Validate trainer_id

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("training_preferences_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "preference_id": preference_id}

    try:
        cursor.execute(formatted_sql, update_params)
        return get_training_preference_by_id(db_conn, cursor, preference_id)
    except MySQLError as e:
        if e.errno == 1062:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update would cause a duplicate preference slot.")
        if e.errno == 1452 and 'trainer_id' in validated_data:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid trainer_id.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def delete_training_preference(db_conn, cursor, preference_id: int):
    get_training_preference_by_id(db_conn, cursor, preference_id) # Existence check
    sql = get_sql("training_preferences_delete_by_id")
    try:
        cursor.execute(sql, (preference_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Preference ID {preference_id} not found for deletion.")
        return True
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

# --- WeeklySchedule Operations ---
def _check_schedule_overlap(cursor, schedule_data: dict, schedule_id_to_exclude: int = None):
    sql = get_sql("weekly_schedule_check_overlap")
    params = {
        "day_of_week": schedule_data["day_of_week"],
        "week_start_date": schedule_data["week_start_date"],
        "trainer_id": schedule_data["trainer_id"],
        "hall_id": schedule_data["hall_id"],
        "start_time": schedule_data["start_time"],
        "end_time": schedule_data["end_time"],
        "schedule_id_to_exclude": schedule_id_to_exclude
    }
    cursor.execute(sql, params)
    overlap = cursor.fetchone()
    if overlap:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Schedule overlap detected for trainer or hall at this time. Conflicting schedule ID: {overlap['schedule_id']}")


def get_weekly_schedule_by_id(db_conn, cursor, schedule_id: int):
    sql = get_sql("weekly_schedule_get_by_id") # Base get without joins for simple fetch
    try:
        cursor.execute(sql, (schedule_id,))
        schedule = format_records(cursor.fetchone())
        if not schedule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Weekly schedule ID {schedule_id} not found.")
        return schedule
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_weekly_schedule_by_week(db_conn, cursor, week_start_date: str, trainer_id: int = None, hall_id: int = None):
    if trainer_id:
        sql = get_sql("weekly_schedule_get_by_trainer_and_week")
        params = {"trainer_id": trainer_id, "week_start_date": week_start_date}
    elif hall_id:
        sql = get_sql("weekly_schedule_get_by_hall_and_week")
        params = {"hall_id": hall_id, "week_start_date": week_start_date}
    else:
        sql = get_sql("weekly_schedule_get_by_week")
        params = (week_start_date,)
    try:
        cursor.execute(sql, params)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def create_weekly_schedule(db_conn, cursor, schedule_data: dict):
    required_fields = ["week_start_date", "day_of_week", "start_time", "end_time", "hall_id", "trainer_id", "max_capacity", "created_by"]
    optional_fields = ["status"]
    try:
        validated_data = validate_payload(schedule_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault("status", "Scheduled")
    # Validate hall_id, trainer_id, created_by (user_id) exist
    # crud_halls.get_hall_by_id(...)
    # crud_user.get_trainer_by_id_pk(...)
    # crud_user.get_user_by_id_pk(...)

    _check_schedule_overlap(cursor, validated_data) # Check for overlaps before creating

    sql = get_sql("weekly_schedule_create")
    try:
        cursor.execute(sql, validated_data)
        schedule_id = cursor.lastrowid
        if not schedule_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create weekly schedule.")
        return get_weekly_schedule_by_id(db_conn, cursor, schedule_id) # Return simple version
    except MySQLError as e:
        if e.errno == 1452: # FK violation
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid hall_id, trainer_id, or created_by user_id.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_weekly_schedule(db_conn, cursor, schedule_id: int, schedule_data: dict):
    existing_schedule = get_weekly_schedule_by_id(db_conn, cursor, schedule_id) # Existence check
    optional_fields = ["week_start_date", "day_of_week", "start_time", "end_time", "hall_id", "trainer_id", "max_capacity", "status"]
    try:
        validated_data = validate_payload(schedule_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for update.")

    # Prepare data for overlap check, using existing values if not provided in update
    overlap_check_data = {
        "week_start_date": validated_data.get("week_start_date", existing_schedule["week_start_date"]),
        "day_of_week": validated_data.get("day_of_week", existing_schedule["day_of_week"]),
        "start_time": validated_data.get("start_time", existing_schedule["start_time"]),
        "end_time": validated_data.get("end_time", existing_schedule["end_time"]),
        "hall_id": validated_data.get("hall_id", existing_schedule["hall_id"]),
        "trainer_id": validated_data.get("trainer_id", existing_schedule["trainer_id"]),
    }
    _check_schedule_overlap(cursor, overlap_check_data, schedule_id_to_exclude=schedule_id)

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("weekly_schedule_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "schedule_id": schedule_id}

    try:
        cursor.execute(formatted_sql, update_params)
        return get_weekly_schedule_by_id(db_conn, cursor, schedule_id)
    except MySQLError as e:
        if e.errno == 1452:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid hall_id or trainer_id during update.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def delete_weekly_schedule(db_conn, cursor, schedule_id: int):
    get_weekly_schedule_by_id(db_conn, cursor, schedule_id) # Existence check
    # ON DELETE CASCADE should handle schedule_members, live_sessions, live_session_attendance
    sql = get_sql("weekly_schedule_delete_by_id")
    try:
        cursor.execute(sql, (schedule_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Weekly schedule ID {schedule_id} not found.")
        return True
    except MySQLError as e:
        if e.errno == 1451: # Should be handled by CASCADE if setup correctly
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete schedule ID {schedule_id}: referenced by other records (ensure ON DELETE CASCADE is setup for child tables like schedule_members).")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")


# --- ScheduleMembers Operations ---
def get_schedule_member_by_id(db_conn, cursor, sm_id: int): # sm_id is the PK of schedule_members
    sql = get_sql("schedule_members_get_by_id")
    try:
        cursor.execute(sql, (sm_id,))
        record = format_records(cursor.fetchone())
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Schedule member link ID {sm_id} not found.")
        return record
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_schedule_members_by_schedule_id(db_conn, cursor, schedule_id: int):
    sql = get_sql("schedule_members_get_by_schedule_id")
    try:
        cursor.execute(sql, (schedule_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_schedule_members_by_member_id_and_week(db_conn, cursor, member_id: int, week_start_date: str):
    """Get all schedule entries for a specific member for a given week"""
    sql = get_sql("schedule_members_get_by_member_id_and_week")
    try:
        cursor.execute(sql, {"member_id": member_id, "week_start_date": week_start_date})
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def add_member_to_schedule(db_conn, cursor, sm_data: dict):
    required_fields = ["schedule_id", "member_id"]
    optional_fields = ["status", "training_plan_day_id"]
    try:
        validated_data = validate_payload(sm_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault("status", "Assigned")
    
    schedule_info = get_weekly_schedule_by_id(db_conn, cursor, validated_data['schedule_id'])
    # crud_user.get_member_by_id_pk(db_conn, cursor, validated_data['member_id']) # Validate member
    if validated_data.get('training_plan_day_id'):
        crud_blueprints.get_training_plan_day_by_id(db_conn, cursor, validated_data['training_plan_day_id'])

    # Check capacity
    count_sql = get_sql("schedule_members_get_count_by_schedule_id_active_status")
    cursor.execute(count_sql, (validated_data['schedule_id'],))
    count_result = cursor.fetchone()
    current_members = count_result['member_count'] if count_result else 0

    if current_members >= schedule_info['max_capacity']:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Schedule slot ID {schedule_info['schedule_id']} is full.")

    sql = get_sql("schedule_members_create")
    try:
        cursor.execute(sql, validated_data)
        sm_id = cursor.lastrowid
        if not sm_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add member to schedule.")
        return get_schedule_member_by_id(db_conn, cursor, sm_id)
    except MySQLError as e:
        if e.errno == 1062: # UNIQUE (schedule_id, member_id)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member already booked for this schedule slot.")
        if e.errno == 1452: # FK violation
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid schedule_id, member_id, or training_plan_day_id.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_schedule_member(db_conn, cursor, sm_id: int, sm_data: dict):
    get_schedule_member_by_id(db_conn, cursor, sm_id) # Existence check
    optional_fields = ["status", "training_plan_day_id"] # Member & schedule usually not changed here
    try:
        validated_data = validate_payload(sm_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for update.")

    if validated_data.get('training_plan_day_id'):
        crud_blueprints.get_training_plan_day_by_id(db_conn, cursor, validated_data['training_plan_day_id'])

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("schedule_members_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "id": sm_id}

    try:
        cursor.execute(formatted_sql, update_params)
        return get_schedule_member_by_id(db_conn, cursor, sm_id)
    except MySQLError as e:
        if e.errno == 1452 and 'training_plan_day_id' in validated_data:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid training_plan_day_id.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def remove_member_from_schedule(db_conn, cursor, sm_id: int):
    get_schedule_member_by_id(db_conn, cursor, sm_id) # Existence check
    sql = get_sql("schedule_members_delete_by_id")
    try:
        cursor.execute(sql, (sm_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Schedule member link ID {sm_id} not found.")
        return True
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")  


def batch_upsert_training_preferences(db_conn, cursor, member_id: int, week_start_date: str, preferences_list: List[Dict]):
    # This function will delete all existing preferences for the member and week,
    # then insert all new ones. This is a common "replace all" strategy for batch.
    # Alternatively, one could try to update existing and insert new, which is more complex.

    # Validate member_id
    # crud_user.get_member_by_id_pk(db_conn, cursor, member_id) 

    # Step 1: Delete existing preferences for this member and week
    delete_sql = get_sql("training_preferences_delete_by_member_and_week")
    try:
        cursor.execute(delete_sql, {"member_id": member_id, "week_start_date": week_start_date})
        # No need to check rowcount, it's fine if none existed
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error deleting old preferences: {str(e)}")

    # Step 2: Insert new preferences
    created_preferences = []
    if not preferences_list: # If empty list provided, it means clear all preferences
        return []

    create_sql = get_sql("training_preferences_create")
    required_pref_fields = ["day_of_week", "start_time", "end_time", "preference_type"]
    optional_pref_fields = ["trainer_id"]

    for pref_data in preferences_list:
        try:
            # Add member_id and week_start_date from function params, not expecting in each pref_data item
            full_pref_data = {
                "member_id": member_id,
                "week_start_date": week_start_date,
                **pref_data # Spread the individual preference data
            }
            validated_data = validate_payload(full_pref_data, 
                                                ["member_id", "week_start_date"] + required_pref_fields, 
                                                optional_pref_fields)
        except ValueError as e:
            # Skip this invalid preference data or raise an error for the whole batch
            print(f"Skipping invalid preference data: {pref_data} due to {str(e)}")
            continue # Or raise HTTPException for the batch

        try:
            cursor.execute(create_sql, validated_data)
            pref_id = cursor.lastrowid
            if pref_id:
                # Fetching each one individually after insert can be slow for large batches.
                # Consider returning the input data with the new ID, or just a success count.
                # For now, let's get the created one for consistency.
                created_preferences.append(get_training_preference_by_id(db_conn, cursor, pref_id))
            else:
                # This shouldn't happen if execute was successful and table has autoincrement
                print(f"Warning: No lastrowid for preference: {validated_data}")
        except MySQLError as e:
            # If one insert fails, the whole transaction (managed by the route) should roll back.
            if e.errno == 1062: # Unique constraint
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Preference slot conflict for {validated_data.get('day_of_week')} {validated_data.get('start_time')}.")
            if e.errno == 1452: # FK (e.g. bad trainer_id if provided)
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid trainer_id for preference.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error inserting preference: {str(e)}")
            
    return created_preferences

def generate_weekly_schedule_for_week(db_conn, cursor, week_start_date_str: str, created_by_user_id: int):
    # This is a placeholder for a complex scheduling algorithm.
    # A real implementation would:
    # 1. Fetch all preferences for the week.
    #    sql_prefs = "SELECT * FROM training_preferences WHERE week_start_date = %s AND preference_type IN ('Preferred', 'Available')"
    #    cursor.execute(sql_prefs, (week_start_date_str,))
    #    preferences = cursor.fetchall()
    #
    # 2. Group preferences by member, then by desired slot (day, time, potentially trainer).
    #
    # 3. For each desired slot/member:
    #    a. Find available trainers (check existing weekly_schedule for conflicts for preferred trainer, or general availability).
    #    b. Find available halls (check existing weekly_schedule for conflicts).
    #    c. If match found:
    #       i. Create a weekly_schedule entry.
    #          schedule_data = { ... "created_by": created_by_user_id ... }
    #          created_schedule = create_weekly_schedule(db_conn, cursor, schedule_data) # This create_weekly_schedule already checks for overlap
    #       ii. Create a schedule_members entry linking the member to this new schedule.
    #           sm_data = {"schedule_id": created_schedule['schedule_id'], "member_id": pref['member_id'], "status": "Assigned"}
    #           add_member_to_schedule(db_conn, cursor, sm_data) # This add_member_to_schedule already checks capacity
    #
    # 4. Handle conflicts, prioritization, fairness etc. (this is the hard part).
    #
    # For this example, we'll just return a success message.
    # In a real system, this function would modify the database and potentially return stats.
    
    print(f"Placeholder: Schedule generation initiated for week {week_start_date_str} by user {created_by_user_id}.")
    # Simulate some action
    # Example: Check if any preferences exist for that week.
    sql_prefs_exist = get_sql("training_preferences_check_for_week") # Needs: SELECT 1 FROM training_preferences WHERE week_start_date = %s LIMIT 1;
    try:
        cursor.execute(sql_prefs_exist, (week_start_date_str,))
        if not cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No training preferences found for week {week_start_date_str} to generate a schedule from.")
    except MySQLError as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error checking preferences: {str(e)}")

    # Actual generation logic would go here.
    # If successful, it would have made INSERTs. The commit is handled by the route.
    
    return {"message": f"Schedule generation process initiated for week {week_start_date_str}. Check the schedule to see results."}