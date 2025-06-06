from typing import Optional
from backend.database.db_utils import get_sql, format_records, validate_payload
from mysql.connector import Error as MySQLError
from fastapi import HTTPException, status
import datetime

# from backend.database.crud import user as crud_user # For FK validation if needed
# from backend.database.crud import training_blueprints as crud_blueprints # For FK validation if needed

# --- EmailNotification Operations ---
def get_email_notification_by_id(db_conn, cursor, notification_id: int):
    sql = get_sql("email_notifications_get_by_id")
    try:
        cursor.execute(sql, (notification_id,))
        record = format_records(cursor.fetchone())
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Email notification ID {notification_id} not found.")
        return record
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_email_notifications_by_user_id(db_conn, cursor, user_id: int):
    # crud_user.get_user_by_id_pk(db_conn, cursor, user_id) # Validate user
    sql = get_sql("email_notifications_get_by_user_id")
    try:
        cursor.execute(sql, (user_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def create_email_notification(db_conn, cursor, notification_data: dict):
    required_fields = ["user_id", "subject", "message", "related_type"]
    optional_fields = ["status", "related_id", "sent_at"]
    try:
        validated_data = validate_payload(notification_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault("status", "Pending")
    validated_data.setdefault("sent_at", datetime.datetime.now())
    # crud_user.get_user_by_id_pk(db_conn, cursor, validated_data['user_id'])

    sql = get_sql("email_notifications_create")
    try:
        cursor.execute(sql, validated_data)
        notification_id = cursor.lastrowid
        if not notification_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create email notification.")
        return get_email_notification_by_id(db_conn, cursor, notification_id)
    except MySQLError as e:
        if e.errno == 1452: # FK for user_id
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id for notification.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_email_notification_status(db_conn, cursor, notification_id: int, new_status: str):
    get_email_notification_by_id(db_conn, cursor, notification_id) # Existence check
    # Validate new_status against ENUMs if necessary
    sql = get_sql("email_notifications_update_status_by_id")
    try:
        cursor.execute(sql, {"status": new_status, "notification_id": notification_id})
        return get_email_notification_by_id(db_conn, cursor, notification_id)
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")


# --- CustomPlanRequest Operations ---
def get_custom_plan_request_by_id(db_conn, cursor, request_id: int):
    sql = get_sql("custom_plan_requests_get_by_id") # This SQL has joins for names
    try:
        cursor.execute(sql, (request_id,))
        record = format_records(cursor.fetchone())
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Custom plan request ID {request_id} not found.")
        return record
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_custom_plan_requests_by_member(db_conn, cursor, member_id: int):
    # crud_user.get_member_by_id_pk(db_conn, cursor, member_id) # Validate member
    sql = get_sql("custom_plan_requests_get_by_member_id")
    try:
        cursor.execute(sql, (member_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_custom_plan_requests_by_assignee(db_conn, cursor, trainer_id: int):
    # crud_user.get_trainer_by_id_pk(db_conn, cursor, trainer_id) # Validate trainer
    sql = get_sql("custom_plan_requests_get_by_trainer_id")
    try:
        cursor.execute(sql, (trainer_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def create_custom_plan_request(db_conn, cursor, request_data: dict):
    required_fields = ["member_id", "goal", "days_per_week"]
    optional_fields = ["focus_areas", "equipment_available", "health_limitations", "assigned_trainer_id", "status", "notes"]
    try:
        validated_data = validate_payload(request_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    validated_data.setdefault("status", "Pending")
    # Validate FKs: member_id, assigned_trainer_id if provided
    # crud_user.get_member_by_id_pk(db_conn, cursor, validated_data['member_id'])
    # if validated_data.get('assigned_trainer_id'):
    #     crud_user.get_trainer_by_id_pk(db_conn, cursor, validated_data['assigned_trainer_id'])

    sql = get_sql("custom_plan_requests_create")
    try:
        cursor.execute(sql, validated_data)
        request_id = cursor.lastrowid
        if not request_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create custom plan request.")
        return get_custom_plan_request_by_id(db_conn, cursor, request_id)
    except MySQLError as e:
        if e.errno == 1452:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid member_id or assigned_trainer_id.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_custom_plan_request(db_conn, cursor, request_id: int, request_data: dict):
    get_custom_plan_request_by_id(db_conn, cursor, request_id) # Existence check
    optional_fields = ["goal", "days_per_week", "focus_areas", "equipment_available", "health_limitations", "assigned_trainer_id", "status", "completed_plan_id", "notes"]
    try:
        validated_data = validate_payload(request_data, [], optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields for update.")

    # Validate FKs if changed: assigned_trainer_id, completed_plan_id
    # if validated_data.get('assigned_trainer_id'):
    #     crud_user.get_trainer_by_id_pk(db_conn, cursor, validated_data['assigned_trainer_id'])
    # if validated_data.get('completed_plan_id'):
    #     crud_blueprints.get_training_plan_by_id(db_conn, cursor, validated_data['completed_plan_id'])
        
    set_clauses = ", ".join([f"{key} = %({key})s" for key in validated_data])
    sql_template = get_sql("custom_plan_requests_update_by_id")
    formatted_sql = sql_template.replace("{set_clauses}", set_clauses)
    update_params = {**validated_data, "request_id": request_id}

    try:
        cursor.execute(formatted_sql, update_params)
        return get_custom_plan_request_by_id(db_conn, cursor, request_id)
    except MySQLError as e:
        if e.errno == 1452:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid FK for trainer or completed plan during update.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")


# --- FinancialTransaction Operations ---
def get_financial_transaction_by_id(db_conn, cursor, transaction_id: int):
    sql = get_sql("financial_transactions_get_by_id") # This SQL has joins
    try:
        cursor.execute(sql, (transaction_id,))
        record = format_records(cursor.fetchone())
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Financial transaction ID {transaction_id} not found.")
        return record
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def get_financial_transactions_by_member_id(db_conn, cursor, member_id: int):
    # crud_user.get_member_by_id_pk(db_conn, cursor, member_id) # Validate member
    sql = get_sql("financial_transactions_get_by_member_id")
    try:
        cursor.execute(sql, (member_id,))
        return format_records(cursor.fetchall())
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def create_financial_transaction(db_conn, cursor, transaction_data: dict):
    required_fields = ["transaction_type", "amount", "payment_method"] # member_id is optional at table level
    optional_fields = ["member_id", "transaction_date", "status", "reference_id", "notes"]
    try:
        validated_data = validate_payload(transaction_data, required_fields, optional_fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    validated_data.setdefault("status", "Pending")
    validated_data.setdefault("transaction_date", datetime.datetime.now())
    # if validated_data.get('member_id'):
    #     crud_user.get_member_by_id_pk(db_conn, cursor, validated_data['member_id'])

    sql = get_sql("financial_transactions_create")
    try:
        cursor.execute(sql, validated_data)
        transaction_id = cursor.lastrowid
        if not transaction_id:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create financial transaction.")
        return get_financial_transaction_by_id(db_conn, cursor, transaction_id)
    except MySQLError as e:
        if e.errno == 1452 and 'member_id' in validated_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid member_id for transaction.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")

def update_financial_transaction_status(db_conn, cursor, transaction_id: int, new_status: str, reference_id: Optional[str]=None, notes: Optional[str]=None):
    transaction = get_financial_transaction_by_id(db_conn, cursor, transaction_id) # Existence check
    # Validate new_status against ENUMs if necessary
    
    update_params = {
        "transaction_id": transaction_id,
        "status": new_status,
        "reference_id": reference_id if reference_id is not None else transaction.get('reference_id'),
        "notes": notes if notes is not None else transaction.get('notes')
    }
    sql = get_sql("financial_transactions_update_status_by_id")
    try:
        cursor.execute(sql, update_params)
        return get_financial_transaction_by_id(db_conn, cursor, transaction_id)
    except MySQLError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {str(e)}")