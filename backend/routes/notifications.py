from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.database.base import get_db_cursor, get_db_connection
from backend.database.crud import miscellaneous as crud_misc # Assuming combined CRUD
from mysql.connector import Error as MySQLError
from typing import Optional

router = APIRouter(prefix="/notifications", tags=["Email Notifications"])

@router.post("/email", status_code=status.HTTP_201_CREATED)
async def create_email_notification_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization if needed (e.g., system internal, or specific roles)
        new_notification = crud_misc.create_email_notification(db_conn, cursor, payload)
        db_conn.commit()
        return new_notification
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e: # Catch specific DB errors
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@router.get("/email/{notification_id}")
def get_email_notification_route(notification_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_misc.get_email_notification_by_id(db_conn, cursor, notification_id)

@router.get("/email/user/{user_id}")
def get_user_email_notifications_route(user_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization: user sees their own, admin sees all
    return crud_misc.get_email_notifications_by_user_id(db_conn, cursor, user_id)

@router.put("/email/{notification_id}/status")
async def update_email_notification_status_route(notification_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json() # Expected: {"status": "new_status"}
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        if "status" not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New status is required.")
        # Add authorization
        updated_notification = crud_misc.update_email_notification_status(db_conn, cursor, notification_id, payload["status"])
        db_conn.commit()
        return updated_notification
    except HTTPException:
        if db_conn: db_conn.rollback()
        raise
    # ... (similar error handling) ...
    finally:
        if cursor: cursor.close()