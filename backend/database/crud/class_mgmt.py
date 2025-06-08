from backend.database.db_utils import get_sql, format_records, validate_payload
from mysql.connector import Error as MySQLError
from fastapi import HTTPException, status

# --- ClassType Operations ---
def get_class_type_by_id(db_conn, cursor, class_type_id: int):
    sql = get_sql("class_types_get_by_id") # Key: filename_queryname
    try:
        cursor.execute(sql, (class_type_id,))
        result = format_records(cursor.fetchone())
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class type with ID {class_type_id} not found")
        return result
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error getting class type: {str(e)}")

def get_all_class_types(db_conn, cursor):
    sql = get_sql("class_types_get_all")
    try:
        cursor.execute(sql)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error getting all class types: {str(e)}")

def create_class_type(db_conn, cursor, class_type_data: dict):
    required_fields = ['name', 'duration_minutes', 'default_price'] # From used_tables.txt
    optional_fields = ['description', 'difficulty_level', 'equipment_needed', 'default_max_participants', 'is_active']
    try:
        validated_data = validate_payload(class_type_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Class type data validation error: {str(e)}")

    validated_data.setdefault('difficulty_level', 'All Levels')
    validated_data.setdefault('is_active', True)
    
    sql = get_sql("class_types_create")
    try:
        cursor.execute(sql, validated_data)
        class_type_id = cursor.lastrowid
        if not class_type_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create class type, no ID returned.")
        return get_class_type_by_id(db_conn, cursor, class_type_id)
    except MySQLError as e:
        if e.errno == 1062: # Duplicate entry for name if name is UNIQUE
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Class type with name '{validated_data.get('name')}' already exists.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error creating class type: {str(e)}")

def update_class_type(db_conn, cursor, class_type_id: int, class_type_data: dict):
    get_class_type_by_id(db_conn, cursor, class_type_id) # Existence check

    optional_fields = ['name', 'description', 'duration_minutes', 'difficulty_level', 'equipment_needed', 'default_max_participants', 'default_price', 'is_active']
    try:
        validated_data = validate_payload(class_type_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Class type update data validation error: {str(e)}")

    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields provided for class type update.")

    set_clauses = ", ".join([f"`{key}` = %({key})s" for key in validated_data]) # Backtick keys just in case
    sql_template = get_sql("class_types_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "class_type_id": class_type_id}
    
    try:
        cursor.execute(formatted_sql, update_params)
        return get_class_type_by_id(db_conn, cursor, class_type_id)
    except MySQLError as e:
        if e.errno == 1062 and 'name' in validated_data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Class type name '{validated_data.get('name')}' already exists for another record.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error updating class type: {str(e)}")

def delete_class_type(db_conn, cursor, class_type_id: int):
    get_class_type_by_id(db_conn, cursor, class_type_id) # Existence check
    sql = get_sql("class_types_delete_by_id")
    try:
        cursor.execute(sql, (class_type_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class type ID {class_type_id} not found for deletion (or already deleted).")
        return True
    except MySQLError as e:
        if e.errno == 1451: # FK constraint violation
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete class type ID {class_type_id}: it is referenced by existing classes.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error deleting class type: {str(e)}")

# --- Class Operations ---
# Assuming the SQL file for classes is named 'classes.sql' to avoid ambiguity with the module.
# If it's 'classes.sql', then keys would be "classes_get_by_id", etc.
# For this example, I'll assume the SQL file is 'classes.sql'
# If your file is classes.sql, change "classes_..." to "classes_..." in get_sql calls below.

def get_class_by_id(db_conn, cursor, class_id: int):
    sql = get_sql("classes_get_by_id") 
    try:
        cursor.execute(sql, (class_id,))
        result = format_records(cursor.fetchone())
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found")
        return result
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error getting class: {str(e)}")

def get_class_detailed_by_id(db_conn, cursor, class_id: int):
    sql = get_sql("classes_get_detailed_by_id")
    try:
        cursor.execute(sql, (class_id,))
        result = format_records(cursor.fetchone())
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Detailed class with ID {class_id} not found")
        return result
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error getting detailed class: {str(e)}")

def get_all_classes(db_conn, cursor, detailed: bool = False):
    sql_key = "classes_get_all_detailed" if detailed else "classes_get_all"
    sql = get_sql(sql_key)
    try:
        cursor.execute(sql)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error getting classes: {str(e)}")

def create_class(db_conn, cursor, class_data: dict):
    required_fields = ['class_type_id', 'trainer_id', 'hall_id', 'date', 'start_time', 'end_time', 'max_participants', 'price']
    optional_fields = ['current_participants', 'status', 'notes']
    try:
        validated_data = validate_payload(class_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Class data validation error: {str(e)}")

    validated_data.setdefault('current_participants', 0)
    validated_data.setdefault('status', 'Scheduled')
    
    sql = get_sql("classes_create")
    try:
        cursor.execute(sql, validated_data)
        class_id = cursor.lastrowid
        if not class_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create class, no ID returned.")
        return get_class_by_id(db_conn, cursor, class_id)
    except MySQLError as e:
        if e.errno == 1452: # FK violation
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid class_type_id, trainer_id, or hall_id.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error creating class: {str(e)}")

def update_class(db_conn, cursor, class_id: int, class_data: dict):
    get_class_by_id(db_conn, cursor, class_id) # Existence check
    optional_fields = ['class_type_id', 'trainer_id', 'hall_id', 'date', 'start_time', 'end_time', 'max_participants', 'current_participants', 'price', 'status', 'notes']
    try:
        validated_data = validate_payload(class_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Class update data validation error: {str(e)}")
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields provided for class update.")

    set_clauses = ", ".join([f"`{key}` = %({key})s" for key in validated_data])
    sql_template = get_sql("classes_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "class_id": class_id}
    
    try:
        cursor.execute(formatted_sql, update_params)
        return get_class_by_id(db_conn, cursor, class_id)
    except MySQLError as e:
        if e.errno == 1452:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid FK in class update (class_type, trainer, or hall).")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error updating class: {str(e)}")

def delete_class(db_conn, cursor, class_id: int):
    get_class_by_id(db_conn, cursor, class_id) # Existence check
    sql = get_sql("classes_delete_by_id")
    try:
        cursor.execute(sql, (class_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class ID {class_id} not found for deletion.")
        return True
    except MySQLError as e:
        if e.errno == 1451: # FK from class_bookings
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete class ID {class_id}: it has existing bookings.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error deleting class: {str(e)}")

def get_classes_by_filter(db_conn, cursor, filter_by: str, filter_id: int):
    if filter_by == "trainer":
        sql_key = "classes_get_by_trainer_id"
    elif filter_by == "hall":
        sql_key = "classes_get_by_hall_id"
    else:
        raise ValueError("Invalid filter_by value for classes.")
    sql = get_sql(sql_key)
    try:
        cursor.execute(sql, (filter_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error getting classes by {filter_by}: {str(e)}")


def get_classes_by_date_range(db_conn, cursor, start_date: str, end_date: str):
    sql = get_sql("classes_get_by_date_range")
    try:
        cursor.execute(sql, {"start_date": start_date, "end_date": end_date})
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error getting classes by date range: {str(e)}")


# --- ClassBooking Operations ---
def get_class_booking_by_id(db_conn, cursor, booking_id: int):
    sql = get_sql("class_bookings_get_by_id")
    try:
        cursor.execute(sql, (booking_id,))
        result = format_records(cursor.fetchone())
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking ID {booking_id} not found.")
        return result
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error getting booking: {str(e)}")

def get_class_bookings_by_class_id(db_conn, cursor, class_id: int):
    get_class_by_id(db_conn, cursor, class_id) # Ensure class exists
    sql = get_sql("class_bookings_get_by_class_id")
    try:
        cursor.execute(sql, (class_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_class_bookings_by_member_id(db_conn, cursor, member_id: int):
    # crud_user.get_member_by_id_pk(db_conn, cursor, member_id) # Validate member
    sql = get_sql("class_bookings_get_by_member_id")
    try:
        cursor.execute(sql, (member_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def create_class_booking(db_conn, cursor, booking_data: dict):
    required_fields = ['class_id', 'member_id', 'payment_status']
    optional_fields = ['amount_paid', 'attendance_status', 'cancellation_date', 'cancellation_reason', 'email_notification_sent']
    try:
        validated_data = validate_payload(booking_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Booking data validation error: {str(e)}")
    
    validated_data.setdefault('attendance_status', 'Not Attended')
    validated_data.setdefault('email_notification_sent', False)
    
    # Capacity Check & FK Validation
    class_info = get_class_by_id(db_conn, cursor, validated_data['class_id'])
    # crud_user.get_member_by_id_pk(db_conn, cursor, validated_data['member_id'])

    count_sql = get_sql("class_bookings_get_count_by_class_id_active_booking")
    cursor.execute(count_sql, (validated_data['class_id'],))
    booking_count_result = cursor.fetchone()
    current_active_bookings = booking_count_result['booking_count'] if booking_count_result else 0
    
    if current_active_bookings >= class_info['max_participants']:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Class is full ({current_active_bookings}/{class_info['max_participants']}).")
        
    sql = get_sql("class_bookings_create")
    try:
        cursor.execute(sql, validated_data)
        booking_id = cursor.lastrowid
        if not booking_id:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create booking.")
        # Update class current_participants
        update_class_participant_count(db_conn, cursor, validated_data['class_id'])
        return get_class_booking_by_id(db_conn, cursor, booking_id)
    except MySQLError as e:
        if e.errno == 1062: # UNIQUE (class_id, member_id)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member already booked for this class.")
        if e.errno == 1452: # FK
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid class_id or member_id.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error creating booking: {str(e)}")

def update_class_booking(db_conn, cursor, booking_id: int, booking_data: dict):
    get_class_booking_by_id(db_conn, cursor, booking_id) # Existence check
    optional_fields = ['payment_status', 'amount_paid', 'attendance_status', 'cancellation_date', 'cancellation_reason', 'email_notification_sent']
    try:
        validated_data = validate_payload(booking_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Booking update data validation error: {str(e)}")
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for booking update.")
    
    set_clauses = ", ".join([f"`{key}` = %({key})s" for key in validated_data])
    sql_template = get_sql("class_bookings_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "booking_id": booking_id}
    
    try:
        # Get class_id before update if attendance status changes, to update participant count
        original_booking = get_class_booking_by_id(db_conn, cursor, booking_id)
        original_attendance = original_booking.get('attendance_status')
        class_id_for_count_update = original_booking.get('class_id')

        cursor.execute(formatted_sql, update_params)
        
        # If attendance status changed, update class participant count
        new_attendance = validated_data.get('attendance_status')
        if new_attendance and new_attendance != original_attendance and class_id_for_count_update:
            update_class_participant_count(db_conn, cursor, class_id_for_count_update)

        return get_class_booking_by_id(db_conn, cursor, booking_id)
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error updating booking: {str(e)}")

def delete_class_booking(db_conn, cursor, booking_id: int):
    booking_to_delete = get_class_booking_by_id(db_conn, cursor, booking_id) # Existence and get class_id
    sql = get_sql("class_bookings_delete_by_id")
    try:
        cursor.execute(sql, (booking_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking ID {booking_id} not found for deletion.")
        # Update class current_participants
        if booking_to_delete and booking_to_delete.get('class_id'):
            # Only decrement if the booking was counted (e.g., not already 'Cancelled')
            if booking_to_delete.get('attendance_status') != 'Cancelled' and booking_to_delete.get('payment_status') in ('Paid', 'Free'):
                 update_class_participant_count(db_conn, cursor, booking_to_delete['class_id'])
        return True
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error deleting booking: {str(e)}")

def update_class_participant_count(db_conn, cursor, class_id: int):
    """Helper to recalculate and update current_participants for a class."""
    count_sql = get_sql("class_bookings_get_count_by_class_id_active_booking")
    try:
        cursor.execute(count_sql, (class_id,))
        count_result = cursor.fetchone()
        current_participants = count_result['booking_count'] if count_result else 0
        
        update_sql = get_sql("classes_update_current_participants") # Needs SQL: UPDATE classes SET current_participants = %(current_participants)s WHERE class_id = %(class_id)s
        cursor.execute(update_sql, {"current_participants": current_participants, "class_id": class_id})
    except MySQLError as e:
        # Log this error but don't necessarily halt the primary operation if it's just a count update
        print(f"Error updating participant count for class {class_id}: {e}")
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error updating participant count: {str(e)}")