from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.database.base import get_db_cursor, get_db_connection
from backend.database.crud import miscellaneous as crud_misc
from mysql.connector import Error as MySQLError
from typing import Optional, List

router = APIRouter(prefix="/finance", tags=["Financial Transactions"])

@router.post("/transactions", status_code=status.HTTP_201_CREATED)
async def create_financial_transaction_route(request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json()
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization: only specific roles (e.g., manager, system)
        new_transaction = crud_misc.create_financial_transaction(db_conn, cursor, payload)
        db_conn.commit()
        return new_transaction
    except HTTPException: # ... (full error handling block) ...
        if db_conn: db_conn.rollback()
        raise
    # ... (similar error handling) ...
    finally:
        if cursor: cursor.close()

@router.get("/transactions/{transaction_id}")
def get_financial_transaction_route(transaction_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization
    return crud_misc.get_financial_transaction_by_id(db_conn, cursor, transaction_id)

@router.get("/transactions/member/{member_id}")
def get_member_financial_transactions_route(member_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    # Add authorization
    return crud_misc.get_financial_transactions_by_member_id(db_conn, cursor, member_id)

@router.get("/transactions") # General query endpoint
def query_financial_transactions_route(
    status_filter: Optional[str] = None, # Renamed to avoid conflict
    type_filter: Optional[str] = None,   # Renamed
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_conn_cursor = Depends(get_db_cursor)
):
    db_conn, cursor = db_conn_cursor
    # This route would require more complex querying logic in CRUD or here.
    # For now, demonstrating one filter example.
    if status_filter:
        # Add SQL 'financial_transactions_get_by_status' and CRUD function
        # return crud_misc.get_financial_transactions_by_status(db_conn, cursor, status_filter)
        raise HTTPException(status_code=501, detail="Filtering by status not yet fully implemented.")
    # ... add logic for other filters or combinations ...
    # else:
    #     return crud_misc.get_all_financial_transactions(db_conn, cursor) # If no filters
    raise HTTPException(status_code=501, detail="Generic transaction query not yet fully implemented.")


@router.put("/transactions/{transaction_id}/status")
async def update_transaction_status_route(transaction_id: int, request: Request, db_conn = Depends(get_db_connection)):
    payload = await request.json() # Expected: {"status": "new_status", "reference_id": "optional", "notes": "optional"}
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Add authorization
        if "status" not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New status is required.")
        
        updated_transaction = crud_misc.update_financial_transaction_status(
            db_conn, cursor, transaction_id, 
            payload["status"], 
            payload.get("reference_id"), 
            payload.get("notes")
        )
        db_conn.commit()
        return updated_transaction
    except HTTPException: # ... (full error handling block) ...
        if db_conn: db_conn.rollback()
        raise
    # ... (similar error handling) ...
    finally:
        if cursor: cursor.close()