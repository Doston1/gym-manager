from backend.database.db_utils import get_sql, format_records, validate_payload
from mysql.connector import Error as MySQLError
from fastapi import HTTPException, status

# --- GymHours Operations ---
def get_gym_hour_by_id(db_conn, cursor, hours_id: int):
    sql = get_sql("gym_hours_get_by_id")
    try:
        cursor.execute(sql, (hours_id,))
        record = format_records(cursor.fetchone())
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gym hours record ID {hours_id} not found.")
        return record
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_gym_hour_by_day(db_conn, cursor, day_of_week: str):
    # Validate day_of_week if necessary, or let DB ENUM handle it
    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if day_of_week not in valid_days:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid day_of_week: {day_of_week}")
        
    sql = get_sql("gym_hours_get_by_day_of_week")
    try:
        cursor.execute(sql, (day_of_week,))
        record = format_records(cursor.fetchone())
        if not record: # This might be acceptable if a day isn't explicitly set
            return None 
        return record
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_all_gym_hours(db_conn, cursor):
    sql = get_sql("gym_hours_get_all")
    try:
        cursor.execute(sql)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def create_gym_hour(db_conn, cursor, hour_data: dict):
    required_fields = ["day_of_week", "opening_time", "closing_time"]
    optional_fields = ["is_closed", "special_note", "is_holiday"]
    try:
        validated_data = validate_payload(hour_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault("is_closed", False)
    validated_data.setdefault("is_holiday", False)

    sql = get_sql("gym_hours_create")
    try:
        cursor.execute(sql, validated_data)
        hours_id = cursor.lastrowid
        if not hours_id:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create gym hour record.")
        return get_gym_hour_by_id(db_conn, cursor, hours_id)
    except MySQLError as e:
        if e.errno == 1062: # Unique constraint on day_of_week
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Gym hours for '{validated_data.get('day_of_week')}' already exist.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_gym_hour_by_day(db_conn, cursor, day_of_week: str, hour_data: dict):
    # Ensure record for the day exists
    existing_record = get_gym_hour_by_day(db_conn, cursor, day_of_week)
    if not existing_record:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gym hours for day '{day_of_week}' not found. Create it first.")

    # For updating by day_of_week, all fields are essentially updatable for that day's record
    # 'day_of_week' itself is the key and not changed by this function.
    required_fields = ["opening_time", "closing_time"] # Minimum to define hours if not closed
    optional_fields = ["is_closed", "special_note", "is_holiday"]
    try:
        validated_data = validate_payload(hour_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    # Add day_of_week for the WHERE clause of the specific update SQL
    update_params = {**validated_data, "day_of_week": day_of_week}
    
    # Ensure boolean values are correctly passed
    update_params['is_closed'] = validated_data.get('is_closed', existing_record.get('is_closed', False))
    update_params['is_holiday'] = validated_data.get('is_holiday', existing_record.get('is_holiday', False))


    sql = get_sql("gym_hours_update_by_day_of_week")
    try:
        cursor.execute(sql, update_params)
        return get_gym_hour_by_day(db_conn, cursor, day_of_week)
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_gym_hour_by_id(db_conn, cursor, hours_id: int, hour_data: dict):
    get_gym_hour_by_id(db_conn, cursor, hours_id) # Existence check
    optional_fields = ["day_of_week", "opening_time", "closing_time", "is_closed", "special_note", "is_holiday"]
    try:
        validated_data = validate_payload(hour_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for update.")

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("gym_hours_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "hours_id": hours_id}

    try:
        cursor.execute(formatted_sql, update_params)
        return get_gym_hour_by_id(db_conn, cursor, hours_id)
    except MySQLError as e:
        if e.errno == 1062 and 'day_of_week' in validated_data: # Unique constraint
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Gym hours for '{validated_data.get('day_of_week')}' already exist for another record.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def delete_gym_hour(db_conn, cursor, hours_id: int): # Typically by ID
    get_gym_hour_by_id(db_conn, cursor, hours_id) # Existence check
    sql = get_sql("gym_hours_delete_by_id")
    try:
        cursor.execute(sql, (hours_id,))
        if cursor.rowcount == 0:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gym hours ID {hours_id} not found for deletion.")
        return True
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")


# --- Hall Operations ---
def get_hall_by_id(db_conn, cursor, hall_id: int):
    sql = get_sql("halls_get_by_id")
    try:
        cursor.execute(sql, (hall_id,))
        hall = format_records(cursor.fetchone())
        if not hall:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Hall ID {hall_id} not found.")
        return hall
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_all_halls(db_conn, cursor, is_active: bool = None):
    params = ()
    if is_active is not None:
        sql = get_sql("halls_get_all_active") # This query should be `SELECT ... WHERE is_active = TRUE`
                                            # If you need dynamic active status, adjust SQL or logic here.
                                            # For now, assuming `halls_get_all_active` implies `is_active = TRUE`
        if not is_active: # If specifically asking for inactive, this query might not be right
            # You might need a new SQL query like `halls_get_all_by_active_status`
            # For simplicity, if is_active=False, we fetch all and filter, or adjust SQL.
            # Let's assume `halls_get_all_active` is for TRUE, and `halls_get_all` for everything.
            # This implementation will use 'halls_get_all_active' only if is_active is True.
            if is_active: # only use this if specifically True
                 sql = get_sql("halls_get_all_active")
            else: # if is_active is False, or None, use get_all
                 sql = get_sql("halls_get_all") # And then filter in Python IF is_active is False
    else:
        sql = get_sql("halls_get_all")

    try:
        cursor.execute(sql, params) # params might be empty if is_active is None
        results = format_records(cursor.fetchall())
        if is_active is False: # Manual filter if SQL for active=FALSE not present
            results = [r for r in results if not r.get('is_active')]
        return results
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")


def create_hall(db_conn, cursor, hall_data: dict):
    required_fields = ["name", "max_capacity"]
    optional_fields = ["description", "location", "equipment_available", "is_active"]
    try:
        validated_data = validate_payload(hall_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault("is_active", True)

    sql = get_sql("halls_create")
    try:
        cursor.execute(sql, validated_data)
        hall_id = cursor.lastrowid
        if not hall_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create hall.")
        return get_hall_by_id(db_conn, cursor, hall_id)
    except MySQLError as e:
        if e.errno == 1062 and 'name' in validated_data: # Assuming name is unique
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Hall with name '{validated_data.get('name')}' already exists.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_hall(db_conn, cursor, hall_id: int, hall_data: dict):
    get_hall_by_id(db_conn, cursor, hall_id) # Existence check
    optional_fields = ["name", "description", "max_capacity", "location", "equipment_available", "is_active"]
    try:
        validated_data = validate_payload(hall_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for update.")

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("halls_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "hall_id": hall_id}

    try:
        cursor.execute(formatted_sql, update_params)
        return get_hall_by_id(db_conn, cursor, hall_id)
    except MySQLError as e:
        if e.errno == 1062 and 'name' in validated_data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Hall name '{validated_data.get('name')}' already exists.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def delete_hall(db_conn, cursor, hall_id: int):
    get_hall_by_id(db_conn, cursor, hall_id) # Existence check
    sql = get_sql("halls_delete_by_id")
    try:
        cursor.execute(sql, (hall_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Hall ID {hall_id} not found for deletion.")
        return True
    except MySQLError as e:
        if e.errno == 1451: # FK constraint from weekly_schedule or classes
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete hall ID {hall_id}: it is used in schedules or classes.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")