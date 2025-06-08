from backend.database.db_utils import get_sql, format_records, validate_payload
from mysql.connector import Error as MySQLError # Correct import
from fastapi import HTTPException

# --- User Operations ---
def get_user_by_auth_id(db_conn, cursor, auth_id: str):
    sql = get_sql("users_get_by_auth_id")
    cursor.execute(sql, (auth_id,))
    user = cursor.fetchone()
    return format_records(user)

def get_user_by_email(db_conn, cursor, email: str):
    sql = get_sql("users_get_by_email")
    cursor.execute(sql, (email,))
    user = cursor.fetchone()
    return format_records(user)

def get_user_by_id_pk(db_conn, cursor, user_id_pk: int):
    sql = get_sql("users_get_by_id_pk")
    cursor.execute(sql, (user_id_pk,))
    user = cursor.fetchone()
    return format_records(user)

def get_users(db_conn, cursor, skip: int = 0, limit: int = 100):
    sql = get_sql("users_get_all")
    cursor.execute(sql, (limit, skip))
    users = cursor.fetchall()
    return format_records(users)

def create_user_and_type(db_conn, user_data: dict):
    required_user_fields = ["auth_id", "email", "first_name", "last_name", "user_type"]
    optional_user_fields = ["phone", "date_of_birth", "gender", "profile_image_path", "is_active"]
    
    try:
        user_payload_for_validation = {k: v for k, v in user_data.items() if k not in ["member_details", "trainer_details", "manager_details"]}
        validated_user_data = validate_payload(user_payload_for_validation, required_user_fields, optional_user_fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"User data validation error: {e}")

    cursor = None # Will be created by db_conn if needed by functions like get_user_by_email
    try:
        # The db_conn itself is passed, and functions inside will get cursor if needed
        # For transactional control, we ensure operations use the SAME connection.
        # If a cursor is needed for multiple ops within this function, create it here from db_conn.
        temp_cursor = db_conn.cursor(dictionary=True) # Temporary for existence checks

        existing_by_email = get_user_by_email(db_conn, temp_cursor, validated_user_data["email"])
        if existing_by_email:
            temp_cursor.close()
            raise HTTPException(status_code=409, detail=f"User with email {validated_user_data['email']} already exists.")
        
        existing_by_auth_id = get_user_by_auth_id(db_conn, temp_cursor, validated_user_data["auth_id"])
        if existing_by_auth_id:
            temp_cursor.close()
            raise HTTPException(status_code=409, detail=f"User with Auth ID {validated_user_data['auth_id']} already exists.")
        
        temp_cursor.close() # Close temp cursor before main operations that might use their own or a new one

        # Main operations, ensuring they use the passed db_conn for transactional integrity
        # Re-create cursor for the actual DML operations
        dml_cursor = db_conn.cursor(dictionary=True)

        sql_user = get_sql("users_create")
        user_insert_params = {
            "auth_id": validated_user_data["auth_id"],
            "email": validated_user_data["email"],
            "first_name": validated_user_data["first_name"],
            "last_name": validated_user_data["last_name"],
            "phone": validated_user_data.get("phone"),
            "date_of_birth": validated_user_data.get("date_of_birth"),
            "gender": validated_user_data.get("gender"),
            "profile_image_path": validated_user_data.get("profile_image_path"),
            "user_type": validated_user_data["user_type"],
            "is_active": validated_user_data.get("is_active", True)
        }
        
        dml_cursor.execute(sql_user, user_insert_params)
        user_id_pk = dml_cursor.lastrowid
        if not user_id_pk:
             db_conn.rollback()
             dml_cursor.close()
             raise HTTPException(status_code=500, detail="Failed to create user record, no ID returned.")
        
        user_type = validated_user_data["user_type"]
        
        if user_type == "member":
            member_details_payload = user_data.get("member_details", {})
            create_member_for_user(db_conn, dml_cursor, user_id_pk, member_details_payload)
        elif user_type == "trainer":
            trainer_details_payload = user_data.get("trainer_details", {})
            create_trainer_for_user(db_conn, dml_cursor, user_id_pk, trainer_details_payload)
        elif user_type == "manager":
            manager_details_payload = user_data.get("manager_details", {})
            create_manager_for_user(db_conn, dml_cursor, user_id_pk, manager_details_payload)

        db_conn.commit()
        
        # Fetch the created user and details for response using the same DML cursor
        created_user_with_details = get_user_by_id_pk(db_conn, dml_cursor, user_id_pk)
        if user_type == "member":
            created_user_with_details["member_details"] = get_member_by_user_id_pk(db_conn, dml_cursor, user_id_pk)
        elif user_type == "trainer":
            created_user_with_details["trainer_details"] = get_trainer_by_user_id_pk(db_conn, dml_cursor, user_id_pk)
        elif user_type == "manager":
            created_user_with_details["manager_details"] = get_manager_by_user_id_pk(db_conn, dml_cursor, user_id_pk)
        
        dml_cursor.close()
        return created_user_with_details
        
    except MySQLError as e: # Use MySQLError
        if db_conn: db_conn.rollback()
        # Close any open cursors if they were created in this block's scope
        if 'temp_cursor' in locals() and temp_cursor and not temp_cursor.is_closed(): temp_cursor.close()
        if 'dml_cursor' in locals() and dml_cursor and not dml_cursor.is_closed(): dml_cursor.close()
        raise HTTPException(status_code=500, detail=f"Database error during user creation: {e}")
    except HTTPException:
        if db_conn: db_conn.rollback()
        if 'temp_cursor' in locals() and temp_cursor and not temp_cursor.is_closed(): temp_cursor.close()
        if 'dml_cursor' in locals() and dml_cursor and not dml_cursor.is_closed(): dml_cursor.close()
        raise
    except Exception as e:
        if db_conn: db_conn.rollback()
        if 'temp_cursor' in locals() and temp_cursor and not temp_cursor.is_closed(): temp_cursor.close()
        if 'dml_cursor' in locals() and dml_cursor and not dml_cursor.is_closed(): dml_cursor.close()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during user creation: {e}")


def update_user_details_by_auth_id(db_conn, cursor, auth_id: str, user_update_data: dict):
    optional_user_fields = ["first_name", "last_name", "phone", "date_of_birth", "gender", "profile_image_path", "is_active"]
    try:
        validated_user_data = validate_payload(user_update_data, [], optional_user_fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not validated_user_data:
        return get_user_by_auth_id(db_conn, cursor, auth_id)

    user = get_user_by_auth_id(db_conn, cursor, auth_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    sql_user_update_template = get_sql("users_update_by_auth_id")
    update_params = {**validated_user_data, "auth_id": auth_id}
    
    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_user_data])
    if not set_clauses:
         return user

    formatted_sql = sql_user_update_template.replace("{set_clauses}", set_clauses)
    
    try:
        cursor.execute(formatted_sql, update_params)
        return get_user_by_auth_id(db_conn, cursor, auth_id)
    except MySQLError as e: # Use MySQLError
        raise HTTPException(status_code=500, detail=f"Database error updating user: {e}")


def delete_user_by_auth_id(db_conn, cursor, auth_id: str):
    user = get_user_by_auth_id(db_conn, cursor, auth_id)
    if not user:
        return False

    sql = get_sql("users_delete_by_auth_id")
    try:
        cursor.execute(sql, (auth_id,))
        return cursor.rowcount > 0
    except MySQLError as e: # Use MySQLError
        raise HTTPException(status_code=500, detail=f"Database error during user deletion: {e}")

# --- Member Operations ---
def get_member_by_user_id_pk(db_conn, cursor, user_id_pk: int):
    sql = get_sql("members_get_by_user_id_pk")
    cursor.execute(sql, (user_id_pk,))
    return format_records(cursor.fetchone())

def create_member_for_user(db_conn, cursor, user_id_pk: int, member_data: dict):
    required_fields = []
    optional_fields = ["weight", "height", "fitness_goal", "fitness_level", "health_conditions"]
    try:
        validated_data = validate_payload(member_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Member data validation error: {e}")

    insert_params = {
        "user_id": user_id_pk,
        "weight": validated_data.get("weight"),
        "height": validated_data.get("height"),
        "fitness_goal": validated_data.get("fitness_goal", "General Fitness"),
        "fitness_level": validated_data.get("fitness_level", "Beginner"),
        "health_conditions": validated_data.get("health_conditions"),
    }
    sql = get_sql("members_create")
    try:
        cursor.execute(sql, insert_params)
    except MySQLError as e: # Use MySQLError
        raise HTTPException(status_code=500, detail=f"Database error creating member record: {e}")


def update_member_details_by_user_id_pk(db_conn, cursor, user_id_pk: int, member_update_data: dict):
    optional_fields = ["weight", "height", "fitness_goal", "fitness_level", "health_conditions"]
    try:
        validated_data = validate_payload(member_update_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not validated_data:
        return get_member_by_user_id_pk(db_conn, cursor, user_id_pk)

    member = get_member_by_user_id_pk(db_conn, cursor, user_id_pk)
    if not member:
        # This case implies an inconsistency: user exists but member record doesn't.
        # For an update, this is an issue. For creation, it's handled elsewhere.
        raise HTTPException(status_code=404, detail="Member record not found for this user to update.")

    sql_template = get_sql("members_update_by_user_id_pk")
    update_params = {**validated_data, "user_id": user_id_pk}
    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    
    if not set_clauses: return member
    
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    try:
        cursor.execute(formatted_sql, update_params)
        return get_member_by_user_id_pk(db_conn, cursor, user_id_pk)
    except MySQLError as e: # Use MySQLError
        raise HTTPException(status_code=500, detail=f"Database error updating member: {e}")

# --- Trainer Operations ---
def get_trainer_by_user_id_pk(db_conn, cursor, user_id_pk: int):
    sql = get_sql("trainers_get_by_user_id_pk")
    cursor.execute(sql, (user_id_pk,))
    return format_records(cursor.fetchone())

def create_trainer_for_user(db_conn, cursor, user_id_pk: int, trainer_data: dict):
    required_fields = [] 
    optional_fields = ["specialization", "bio", "certifications", "years_of_experience"]
    try:
        validated_data = validate_payload(trainer_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Trainer data validation error: {e}")

    insert_params = {
        "trainer_id": user_id_pk,
        "user_id": user_id_pk,
        "specialization": validated_data.get("specialization"),
        "bio": validated_data.get("bio"),
        "certifications": validated_data.get("certifications"),
        "years_of_experience": validated_data.get("years_of_experience")
    }
    sql = get_sql("trainers_create")
    try:
        cursor.execute(sql, insert_params)
    except MySQLError as e: # Use MySQLError
        raise HTTPException(status_code=500, detail=f"Database error creating trainer record: {e}")


def update_trainer_details_by_trainer_id_pk(db_conn, cursor, trainer_id_pk: int, trainer_update_data: dict):
    optional_fields = ["specialization", "bio", "certifications", "years_of_experience"]
    try:
        validated_data = validate_payload(trainer_update_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not validated_data:
        return get_trainer_by_user_id_pk(db_conn, cursor, trainer_id_pk)

    trainer = get_trainer_by_user_id_pk(db_conn, cursor, trainer_id_pk)
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer record not found.")

    sql_template = get_sql("trainers_update_by_trainer_id_pk")
    update_params = {**validated_data, "trainer_id": trainer_id_pk}
    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])

    if not set_clauses: return trainer
    
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    try:
        cursor.execute(formatted_sql, update_params)
        return get_trainer_by_user_id_pk(db_conn, cursor, trainer_id_pk)
    except MySQLError as e: # Use MySQLError
        raise HTTPException(status_code=500, detail=f"Database error updating trainer: {e}")


# --- Manager Operations ---
def get_manager_by_user_id_pk(db_conn, cursor, user_id_pk: int):
    sql = get_sql("managers_get_by_user_id_pk")
    cursor.execute(sql, (user_id_pk,))
    return format_records(cursor.fetchone())

def create_manager_for_user(db_conn, cursor, user_id_pk: int, manager_data: dict):
    required_fields = []
    optional_fields = ["department", "hire_date"]
    try:
        validated_data = validate_payload(manager_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Manager data validation error: {e}")

    insert_params = {
        "manager_id": user_id_pk,
        "user_id": user_id_pk,
        "department": validated_data.get("department"),
        "hire_date": validated_data.get("hire_date")
    }
    sql = get_sql("managers_create")
    try:
        cursor.execute(sql, insert_params)
    except MySQLError as e: # Use MySQLError
        raise HTTPException(status_code=500, detail=f"Database error creating manager record: {e}")

def update_manager_details_by_manager_id_pk(db_conn, cursor, manager_id_pk: int, manager_update_data: dict):
    optional_fields = ["department", "hire_date"]
    try:
        validated_data = validate_payload(manager_update_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not validated_data:
        return get_manager_by_user_id_pk(db_conn, cursor, manager_id_pk)

    manager = get_manager_by_user_id_pk(db_conn, cursor, manager_id_pk)
    if not manager:
        raise HTTPException(status_code=404, detail="Manager record not found.")

    sql_template = get_sql("managers_update_by_manager_id_pk")
    update_params = {**validated_data, "manager_id": manager_id_pk}
    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])

    if not set_clauses: return manager
    
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    try:
        cursor.execute(formatted_sql, update_params)
        return get_manager_by_user_id_pk(db_conn, cursor, manager_id_pk)
    except MySQLError as e: # Use MySQLError
        raise HTTPException(status_code=500, detail=f"Database error updating manager: {e}")