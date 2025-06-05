from backend.database.db_utils import get_sql, format_records, validate_payload
from mysql.connector import Error as MySQLError
from fastapi import HTTPException, status

# --- ClassType Operations ---
def get_class_type_by_id(db_conn, cursor, class_type_id: int):
    sql = get_sql("class_types_get_by_id")
    try:
        cursor.execute(sql, (class_type_id,))
        result = format_records(cursor.fetchone())
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class type with ID {class_type_id} not found")
        return result
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_all_class_types(db_conn, cursor):
    sql = get_sql("class_types_get_all")
    try:
        cursor.execute(sql)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def create_class_type(db_conn, cursor, class_type_data: dict):
    # Validate required fields
    required_fields = ['name', 'description', 'intensity_level']
    optional_fields = []
    validate_payload(class_type_data, required_fields, optional_fields)
    
    sql = get_sql("class_types_create")
    try:
        cursor.execute(sql, class_type_data)
        class_type_id = cursor.lastrowid
        
        # Fetch the newly created class type
        return get_class_type_by_id(db_conn, cursor, class_type_id)
    except MySQLError as e:
        if e.errno == 1062:  # Duplicate entry error code
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Class type with name '{class_type_data['name']}' already exists")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def update_class_type(db_conn, cursor, class_type_id: int, class_type_data: dict):
    # Check if class type exists
    get_class_type_by_id(db_conn, cursor, class_type_id)
    
    # Validate fields
    required_fields = ['name', 'description', 'intensity_level']
    optional_fields = []
    validate_payload(class_type_data, required_fields, optional_fields)
    
    # Add class_type_id to data for the update query
    class_type_data['class_type_id'] = class_type_id
    
    sql = get_sql("class_types_update_by_id")
    try:
        cursor.execute(sql, class_type_data)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class type with ID {class_type_id} not found or no changes made")
        
        # Fetch updated class type
        return get_class_type_by_id(db_conn, cursor, class_type_id)
    except MySQLError as e:
        if e.errno == 1062:  # Duplicate entry error code
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Class type with name '{class_type_data['name']}' already exists")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def delete_class_type(db_conn, cursor, class_type_id: int):
    # Check if class type exists
    get_class_type_by_id(db_conn, cursor, class_type_id)
    
    sql = get_sql("class_types_delete_by_id")
    try:
        cursor.execute(sql, (class_type_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class type with ID {class_type_id} not found")
        return {"message": f"Class type with ID {class_type_id} deleted successfully"}
    except MySQLError as e:
        if e.errno == 1451:  # Foreign key constraint violation
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete class type with ID {class_type_id} as it is referenced by classes")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

# --- Class Operations ---
def get_class_by_id(db_conn, cursor, class_id: int):
    sql = get_sql("classes_get_by_id")
    try:
        cursor.execute(sql, (class_id,))
        result = format_records(cursor.fetchone())
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found")
        return result
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_class_detailed_by_id(db_conn, cursor, class_id: int):
    # First check if the class exists
    get_class_by_id(db_conn, cursor, class_id)
    
    # Get detailed class info
    sql = get_sql("classes_get_all_detailed")
    try:
        cursor.execute(sql)
        all_classes = format_records(cursor.fetchall())
        for class_item in all_classes:
            if class_item['class_id'] == class_id:
                return class_item
        
        # Should not happen if get_class_by_id was successful
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found")
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_all_classes(db_conn, cursor):
    sql = get_sql("classes_get_all")
    try:
        cursor.execute(sql)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_all_classes_detailed(db_conn, cursor):
    sql = get_sql("classes_get_all_detailed")
    try:
        cursor.execute(sql)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def create_class(db_conn, cursor, class_data: dict):
    # Validate required fields
    required_fields = ['class_type_id', 'trainer_id', 'hall_id', 'start_time', 'end_time', 'max_capacity']
    optional_fields = ['description']
    validate_payload(class_data, required_fields, optional_fields)
    
    sql = get_sql("classes_create")
    try:
        cursor.execute(sql, class_data)
        class_id = cursor.lastrowid
        
        # Fetch the newly created class
        return get_class_by_id(db_conn, cursor, class_id)
    except MySQLError as e:
        if e.errno == 1452:  # Foreign key constraint failure
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reference: class_type_id, trainer_id, or hall_id doesn't exist")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def update_class(db_conn, cursor, class_id: int, class_data: dict):
    # Check if class exists
    get_class_by_id(db_conn, cursor, class_id)
    
    # Validate fields
    required_fields = ['class_type_id', 'trainer_id', 'hall_id', 'start_time', 'end_time', 'max_capacity']
    optional_fields = ['description']
    validate_payload(class_data, required_fields, optional_fields)
    
    # Add class_id to data for the update query
    class_data['class_id'] = class_id
    
    sql = get_sql("classes_update_by_id")
    try:
        cursor.execute(sql, class_data)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found or no changes made")
        
        # Fetch updated class
        return get_class_by_id(db_conn, cursor, class_id)
    except MySQLError as e:
        if e.errno == 1452:  # Foreign key constraint failure
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reference: class_type_id, trainer_id, or hall_id doesn't exist")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def delete_class(db_conn, cursor, class_id: int):
    # Check if class exists
    get_class_by_id(db_conn, cursor, class_id)
    
    sql = get_sql("classes_delete_by_id")
    try:
        cursor.execute(sql, (class_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found")
        return {"message": f"Class with ID {class_id} deleted successfully"}
    except MySQLError as e:
        if e.errno == 1451:  # Foreign key constraint violation
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete class with ID {class_id} as it has bookings")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_classes_by_trainer_id(db_conn, cursor, trainer_id: int):
    sql = get_sql("classes_get_by_trainer_id")
    try:
        cursor.execute(sql, (trainer_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_classes_by_hall_id(db_conn, cursor, hall_id: int):
    sql = get_sql("classes_get_by_hall_id")
    try:
        cursor.execute(sql, (hall_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_classes_by_date_range(db_conn, cursor, start_date: str, end_date: str):
    sql = get_sql("classes_get_by_date_range")
    try:
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        cursor.execute(sql, params)
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

# --- ClassBooking Operations ---
def get_class_booking_by_id(db_conn, cursor, booking_id: int):
    sql = get_sql("class_bookings_get_by_id")
    try:
        cursor.execute(sql, (booking_id,))
        result = format_records(cursor.fetchone())
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with ID {booking_id} not found")
        return result
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_class_bookings_by_class_id(db_conn, cursor, class_id: int):
    sql = get_sql("class_bookings_get_by_class_id")
    try:
        cursor.execute(sql, (class_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_class_bookings_by_member_id(db_conn, cursor, member_id: int):
    sql = get_sql("class_bookings_get_by_member_id")
    try:
        cursor.execute(sql, (member_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def create_class_booking(db_conn, cursor, booking_data: dict):
    # Validate required fields
    required_fields = ['class_id', 'member_id']
    optional_fields = ['status', 'attendance']
    validate_payload(booking_data, required_fields, optional_fields)
    
    # Set default values if not provided
    if 'status' not in booking_data:
        booking_data['status'] = 'Confirmed'
    if 'attendance' not in booking_data:
        booking_data['attendance'] = 'Not Checked'
    
    # Check if class exists and has available capacity
    try:
        # Get class details
        class_sql = get_sql("classes_get_by_id")
        cursor.execute(class_sql, (booking_data['class_id'],))
        class_data = format_records(cursor.fetchone())
        if not class_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {booking_data['class_id']} not found")
        
        # Check if class still has capacity
        count_sql = get_sql("class_bookings_get_count_by_class_id")
        cursor.execute(count_sql, (booking_data['class_id'],))
        booking_count = cursor.fetchone()['booking_count']
        
        if booking_count >= class_data['max_capacity']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=f"Class is at full capacity ({booking_count}/{class_data['max_capacity']})")
        
        # Proceed with booking creation
        sql = get_sql("class_bookings_create")
        cursor.execute(sql, booking_data)
        booking_id = cursor.lastrowid
        
        # Fetch the newly created booking
        return get_class_booking_by_id(db_conn, cursor, booking_id)
    except MySQLError as e:
        if e.errno == 1062:  # Duplicate entry error
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"Member {booking_data['member_id']} already has a booking for class {booking_data['class_id']}")
        if e.errno == 1452:  # Foreign key constraint failure
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Invalid reference: class_id or member_id doesn't exist")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def update_class_booking(db_conn, cursor, booking_id: int, booking_data: dict):
    # Check if booking exists
    get_class_booking_by_id(db_conn, cursor, booking_id)
    
    # Validate fields
    required_fields = []
    optional_fields = ['status', 'attendance']
    validate_payload(booking_data, required_fields, optional_fields)
    
    # If no data to update, return early
    if not booking_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    
    # Add booking_id to data for the update query
    booking_data['booking_id'] = booking_id
    
    sql = get_sql("class_bookings_update_by_id")
    try:
        cursor.execute(sql, booking_data)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Booking with ID {booking_id} not found or no changes made")
        
        # Fetch updated booking
        return get_class_booking_by_id(db_conn, cursor, booking_id)
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def delete_class_booking(db_conn, cursor, booking_id: int):
    # Check if booking exists
    get_class_booking_by_id(db_conn, cursor, booking_id)
    
    sql = get_sql("class_bookings_delete_by_id")
    try:
        cursor.execute(sql, (booking_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with ID {booking_id} not found")
        return {"message": f"Booking with ID {booking_id} deleted successfully"}
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")