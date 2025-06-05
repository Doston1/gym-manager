from fastapi import APIRouter, Depends, HTTPException, Request, status
from backend.database.base import get_db_cursor, get_db_connection # Using both for different scenarios
from backend.database.crud import user as crud_user
from mysql.connector import Error as MySQLError # Import the correct error type

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{auth_id_param}")
def get_user_endpoint(auth_id_param: str, db_conn_cursor_tuple = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor_tuple
    try:
        user = crud_user.get_user_by_auth_id(db_conn, cursor, auth_id_param)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Augment with role-specific details
        user_id_pk = user["user_id"]
        if user.get("user_type") == "member":
            member_details = crud_user.get_member_by_user_id_pk(db_conn, cursor, user_id_pk)
            if member_details: user["member_details"] = member_details
        elif user.get("user_type") == "trainer":
            trainer_details = crud_user.get_trainer_by_user_id_pk(db_conn, cursor, user_id_pk)
            if trainer_details: user["trainer_details"] = trainer_details
        elif user.get("user_type") == "manager":
            manager_details = crud_user.get_manager_by_user_id_pk(db_conn, cursor, user_id_pk)
            if manager_details: user["manager_details"] = manager_details
            
        return user
    except MySQLError as e:
        # This catch block is for errors directly from cursor operations in this route, if any.
        # Most DB errors should be caught and re-raised as HTTPExceptions by CRUD functions.
        raise HTTPException(status_code=500, detail=f"Database query error in route: {e}")
    except HTTPException:
        raise # Re-raise HTTPExceptions from CRUD
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error in get_user_endpoint: {e}")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(request: Request, db_conn = Depends(get_db_connection)):
    user_data = await request.json()
    try:
        # create_user_and_type handles its own transaction and cursor management using db_conn
        created_user_with_details = crud_user.create_user_and_type(db_conn, user_data)
        return created_user_with_details
    except MySQLError as e: # Catch DB errors if create_user_and_type doesn't fully abstract them as HTTP
        if db_conn: db_conn.rollback() # Ensure rollback if not handled deeper
        raise HTTPException(status_code=500, detail=f"Database transaction error during creation: {e}")
    except HTTPException:
        # CRUD function should raise HTTPException for validation, etc.
        # If it does, and it manages its own rollback, we just re-raise.
        # If the CRUD function doesn't manage rollback on HTTPException, we might need to do it here.
        # Based on current crud_user, it does handle rollback for HTTPExceptions.
        raise
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error during user creation: {e}")


@router.put("/{auth_id_param}")
async def update_user_endpoint(auth_id_param: str, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    
    user_update_data = {}
    member_update_data = {}
    trainer_update_data = {}
    manager_update_data = {}

    user_keys = ["first_name", "last_name", "phone", "date_of_birth", "gender", "profile_image_path", "is_active"]
    member_keys = ["weight", "height", "fitness_goal", "fitness_level", "health_conditions", "active_cycle_id"]
    trainer_keys = ["specialization", "bio", "certifications", "years_of_experience"]
    manager_keys = ["department", "hire_date"]

    for key, value in payload.items():
        if key in user_keys: user_update_data[key] = value
        elif key in member_keys: member_update_data[key] = value
        elif key in trainer_keys: trainer_update_data[key] = value
        elif key in manager_keys: manager_update_data[key] = value

    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        
        if user_update_data:
            crud_user.update_user_details_by_auth_id(db_conn, cursor, auth_id_param, user_update_data)

        current_user_state = crud_user.get_user_by_auth_id(db_conn, cursor, auth_id_param)
        if not current_user_state:
            raise HTTPException(status_code=404, detail="User not found, cannot update role details.")
        
        user_id_pk = current_user_state["user_id"]
        user_type = current_user_state["user_type"]

        if user_type == "member" and member_update_data:
            crud_user.update_member_details_by_user_id_pk(db_conn, cursor, user_id_pk, member_update_data)
        elif user_type == "trainer" and trainer_update_data:
            crud_user.update_trainer_details_by_trainer_id_pk(db_conn, cursor, user_id_pk, trainer_update_data)
        elif user_type == "manager" and manager_update_data:
            crud_user.update_manager_details_by_manager_id_pk(db_conn, cursor, user_id_pk, manager_update_data)

        db_conn.commit()

        final_user_data = crud_user.get_user_by_auth_id(db_conn, cursor, auth_id_param)
        if not final_user_data:
             raise HTTPException(status_code=404, detail="User disappeared after update.")

        if final_user_data.get("user_type") == "member":
            member_details = crud_user.get_member_by_user_id_pk(db_conn, cursor, final_user_data["user_id"])
            if member_details: final_user_data["member_details"] = member_details
        elif final_user_data.get("user_type") == "trainer":
            trainer_details = crud_user.get_trainer_by_user_id_pk(db_conn, cursor, final_user_data["user_id"])
            if trainer_details: final_user_data["trainer_details"] = trainer_details
        elif final_user_data.get("user_type") == "manager":
            manager_details = crud_user.get_manager_by_user_id_pk(db_conn, cursor, final_user_data["user_id"])
            if manager_details: final_user_data["manager_details"] = manager_details
            
        return final_user_data

    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e: # Catch MySQLError here
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database transaction error: {e}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during update: {e}")
    finally:
        if cursor:
            cursor.close()


@router.delete("/{auth_id_param}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(auth_id_param: str, db_conn = Depends(get_db_connection)):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        success = crud_user.delete_user_by_auth_id(db_conn, cursor, auth_id_param)
        if not success:
            raise HTTPException(status_code=404, detail="User not found or could not be deleted")
        db_conn.commit()
        return None 
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e: # Catch MySQLError here
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during deletion: {e}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error during deletion: {e}")
    finally:
        if cursor:
            cursor.close()