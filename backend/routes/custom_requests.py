from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.database.base import get_db_cursor, get_db_connection
from backend.database.crud import miscellaneous as crud_misc
from mysql.connector import Error as MySQLError
from typing import Optional

router = APIRouter(prefix="/custom-plan-requests", tags=["Custom Plan Requests"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_custom_plan_request_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: member creates for themselves
        # member_id could come from authenticated user context
        new_request = crud_misc.create_custom_plan_request(db_conn, cursor, payload)
        db_conn.commit()
        return new_request
    except HTTPException: # ... (full error handling block as in other POST routes) ...
        if db_conn: db_conn.rollback()
        raise
    except MySQLError as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")
    except Exception as e:
        if db_conn: db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    finally:
        if cursor: cursor.close()

@router.get("/{request_id}")
def get_custom_plan_request_route(request_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization
    return crud_misc.get_custom_plan_request_by_id(db_conn, cursor, request_id)

@router.get("/member/{member_id}")
def get_member_custom_plan_requests_route(member_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization
    return crud_misc.get_custom_plan_requests_by_member(db_conn, cursor, member_id)

@router.get("/trainer/{trainer_id}")
def get_assigned_custom_plan_requests_route(trainer_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization: trainer sees their own assigned
    return crud_misc.get_custom_plan_requests_by_assignee(db_conn, cursor, trainer_id)

@router.get("/") # Get all by status, e.g., for manager overview
def get_all_custom_plan_requests_by_status_route(status_filter: Optional[str] = None, db_conn_cursor = Depends(get_db_cursor)):
    # Renamed `status` to `status_filter` to avoid conflict with FastAPI's status_code
    db_conn, cursor = db_conn_cursor
    if status_filter:
        # Add SQL query 'custom_plan_requests_get_by_status' to your SQL file
        # and corresponding CRUD function
        # return crud_misc.get_custom_plan_requests_by_status(db_conn, cursor, status_filter)
        raise HTTPException(status_code=501, detail="Filtering by status not yet implemented in CRUD.")
    else:
        # Add SQL query 'custom_plan_requests_get_all'
        # return crud_misc.get_all_custom_plan_requests(db_conn, cursor)
        raise HTTPException(status_code=501, detail="Get all custom plan requests not yet implemented in CRUD.")


@router.put("/{request_id}")
async def update_custom_plan_request_route(request_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization (trainer updating assigned request, manager, or member cancelling)
        updated_request = crud_misc.update_custom_plan_request(db_conn, cursor, request_id, payload)
        db_conn.commit()
        return updated_request
    except HTTPException: # ... (full error handling block) ...
        if db_conn: db_conn.rollback()
        raise
    # ... (similar error handling) ...
    finally:
        if cursor: cursor.close()