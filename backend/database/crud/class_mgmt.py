from backend.database.db_utils import get_sql, format_records, validate_payload
from mysql.connector import Error as MySQLError
from fastapi import HTTPException, status

# --- ClassType Operations ---
def get_class_type_by_id(db_conn, cursor, class_type_id: int):
    sql = get_sql("class_types_get_by_id") # Assuming SQL key: class_types_get_by_id
    try:
        cursor.execute(sql, (class_type_id,))
        result = format_records(cursor.fetchone())
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class type with ID {class_type_id} not found")
        return result
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_all_class_types(db_conn, cursor):
    sql = get_sql("class_types_get_all") # Assuming SQL key: class_types_get_all
    try:
        cursor.execute(sql)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def create_class_type(db_conn, cursor, class_type_data: dict):
    # Align with used_tables.txt: class_types
    required_fields = ['name', 'duration_minutes', 'default_price']
    optional_fields = ['description', 'difficulty_level', 'equipment_needed', 'default_max_participants', 'is_active']
    try:
        validated_data = validate_payload(class_type_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault('difficulty_level', 'All Levels')
    validated_data.setdefault('is_active', True)
    
    sql = get_sql("class_types_create") # Assuming SQL key: class_types_create
    try:
        cursor.execute(sql, validated_data) # Pass validated_data
        class_type_id = cursor.lastrowid
        if not class_type_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create class type, no ID returned.")
        # No commit here, handled by route
        return get_class_type_by_id(db_conn, cursor, class_type_id)
    except MySQLError as e:
        if e.errno == 1062:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Class type with name '{validated_data.get('name')}' already exists")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def update_class_type(db_conn, cursor, class_type_id: int, class_type_data: dict):
    # Check if class type exists first (optional, as update can check rowcount)
    # get_class_type_by_id(db_conn, cursor, class_type_id) # This raises 404 if not found

    # Align with used_tables.txt: class_types (all updatable fields)
    optional_fields = ['name', 'description', 'duration_minutes', 'difficulty_level', 'equipment_needed', 'default_max_participants', 'default_price', 'is_active']
    try:
        validated_data = validate_payload(class_type_data, [], optional_fields) # No required for update
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields provided for update.")

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    # Ensure your SQL file for class_types_update_by_id has {set_clauses}
    sql_template = get_sql("class_types_update_by_id") # Assuming SQL key: class_types_update_by_id
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    
    update_params = {**validated_data, "class_type_id": class_type_id}
    
    try:
        cursor.execute(formatted_sql, update_params)
        # if cursor.rowcount == 0:
        #     # This could mean not found OR no actual change.
        #     # Depending on desired behavior, could raise 404 or just return current state.
        #     # For now, assume if execute didn't error, it's fine. The get below will confirm.
        #     pass
        # No commit here, handled by route
        return get_class_type_by_id(db_conn, cursor, class_type_id)
    except MySQLError as e:
        if e.errno == 1062 and 'name' in validated_data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Class type name '{validated_data['name']}' already exists for another record.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def delete_class_type(db_conn, cursor, class_type_id: int):
    # Optional: Check existence first if you want a specific 404 before attempting delete
    # get_class_type_by_id(db_conn, cursor, class_type_id) 
    
    sql = get_sql("class_types_delete_by_id") # Assuming SQL key: class_types_delete_by_id
    try:
        cursor.execute(sql, (class_type_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class type with ID {class_type_id} not found for deletion.")
        # No commit here, handled by route
        return True # Or None, for routes expecting 204
    except MySQLError as e:
        if e.errno == 1451:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete class type ID {class_type_id}: referenced by existing classes.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

# --- Class Operations ---
def get_class_by_id(db_conn, cursor, class_id: int):
    sql = get_sql("classes_get_by_id") # Assuming SQL key
    try:
        cursor.execute(sql, (class_id,))
        result = format_records(cursor.fetchone())
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found")
        return result
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_class_detailed_by_id(db_conn, cursor, class_id: int):
    sql = get_sql("classes_get_detailed_by_id") # Use specific SQL, not get_all_detailed
    try:
        cursor.execute(sql, (class_id,)) # Pass class_id to the SQL query
        result = format_records(cursor.fetchone())
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Detailed class with ID {class_id} not found")
        return result
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_all_classes(db_conn, cursor):
    sql = get_sql("classes_get_all") # Assuming SQL key
    try:
        cursor.execute(sql)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_all_classes_detailed(db_conn, cursor):
    sql = get_sql("classes_get_all_detailed") # Assuming SQL key
    try:
        cursor.execute(sql)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def create_class(db_conn, cursor, class_data: dict):
    # Align with used_tables.txt: classes
    required_fields = ['class_type_id', 'trainer_id', 'hall_id', 'date', 'start_time', 'end_time', 'max_participants', 'price']
    optional_fields = ['current_participants', 'status', 'notes']
    try:
        validated_data = validate_payload(class_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault('current_participants', 0)
    validated_data.setdefault('status', 'Scheduled')
    
    sql = get_sql("classes_create") # Assuming SQL key
    try:
        cursor.execute(sql, validated_data)
        class_id = cursor.lastrowid
        if not class_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create class, no ID returned.")
        # No commit here
        return get_class_by_id(db_conn, cursor, class_id)
    except MySQLError as e:
        if e.errno == 1452:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid foreign key: class_type_id, trainer_id, or hall_id does not exist.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def update_class(db_conn, cursor, class_id: int, class_data: dict):
    # Align with used_tables.txt: classes (all updatable fields)
    optional_fields = ['class_type_id', 'trainer_id', 'hall_id', 'date', 'start_time', 'end_time', 'max_participants', 'current_participants', 'price', 'status', 'notes']
    try:
        validated_data = validate_payload(class_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields provided for update.")

    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("classes_update_by_id") # Assuming SQL key
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    
    update_params = {**validated_data, "class_id": class_id}
    
    try:
        cursor.execute(formatted_sql, update_params)
        # No commit here
        return get_class_by_id(db_conn, cursor, class_id)
    except MySQLError as e:
        if e.errno == 1452:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid foreign key during update: class_type_id, trainer_id, or hall_id does not exist.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def delete_class(db_conn, cursor, class_id: int):
    sql = get_sql("classes_delete_by_id") # Assuming SQL key
    try:
        cursor.execute(sql, (class_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found for deletion.")
        # No commit here
        return True
    except MySQLError as e:
        if e.errno == 1451:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete class ID {class_id}: it has existing bookings.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

# ... (get_classes_by_trainer_id, get_classes_by_hall_id, get_classes_by_date_range are likely okay, ensure SQL keys match)

# --- ClassBooking Operations ---
def get_class_booking_by_id(db_conn, cursor, booking_id: int):
    sql = get_sql("class_bookings_get_by_id") # Assuming SQL key
    try:
        cursor.execute(sql, (booking_id,))
        result = format_records(cursor.fetchone())
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with ID {booking_id} not found")
        return result
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

# ... (get_class_bookings_by_class_id, get_class_bookings_by_member_id are likely okay, ensure SQL keys match)

def create_class_booking(db_conn, cursor, booking_data: dict):
    # Align with used_tables.txt: class_bookings
    required_fields = ['class_id', 'member_id', 'payment_status']
    optional_fields = ['amount_paid', 'attendance_status', 'cancellation_date', 'cancellation_reason', 'email_notification_sent']
    try:
        validated_data = validate_payload(booking_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    validated_data.setdefault('attendance_status', 'Not Attended')
    validated_data.setdefault('email_notification_sent', False)
    
    try:
        # Capacity Check (ensure 'classes_get_by_id' and 'class_bookings_get_count_by_class_id' SQLs exist and work)
        class_info = get_class_by_id(db_conn, cursor, validated_data['class_id']) # This already raises 404 if class not found

        count_sql = get_sql("class_bookings_get_count_by_class_id") # e.g. SELECT COUNT(*) as booking_count FROM class_bookings WHERE class_id = %s
        cursor.execute(count_sql, (validated_data['class_id'],))
        booking_count_result = cursor.fetchone()
        
        current_bookings = 0
        if booking_count_result and 'booking_count' in booking_count_result:
            current_bookings = booking_count_result['booking_count']
        
        if current_bookings >= class_info['max_participants']: # Use max_participants
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=f"Class is at full capacity ({current_bookings}/{class_info['max_participants']})")
        
        sql = get_sql("class_bookings_create") # Assuming SQL key
        cursor.execute(sql, validated_data)
        booking_id = cursor.lastrowid
        if not booking_id:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create booking, no ID returned.")
        # No commit here
        return get_class_booking_by_id(db_conn, cursor, booking_id)
    except MySQLError as e:
        if e.errno == 1062:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"Member {validated_data['member_id']} already booked for class {validated_data['class_id']}.")
        if e.errno == 1452:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Invalid foreign key: class_id or member_id does not exist.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def update_class_booking(db_conn, cursor, booking_id: int, booking_data: dict):
    # Align with used_tables.txt: class_bookings (all updatable fields)
    optional_fields = ['payment_status', 'amount_paid', 'attendance_status', 'cancellation_date', 'cancellation_reason', 'email_notification_sent']
    try:
        validated_data = validate_payload(booking_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields provided for update.")
    
    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("class_bookings_update_by_id") # Assuming SQL key
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    
    update_params = {**validated_data, "booking_id": booking_id}
    
    try:
        cursor.execute(formatted_sql, update_params)
        # No commit here
        return get_class_booking_by_id(db_conn, cursor, booking_id)
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def delete_class_booking(db_conn, cursor, booking_id: int):
    sql = get_sql("class_bookings_delete_by_id") # Assuming SQL key
    try:
        cursor.execute(sql, (booking_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with ID {booking_id} not found for deletion.")
        # No commit here
        return True
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")