from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.database.base import get_db_cursor, get_db_connection
from backend.database.crud import class_mgmt as crud_class

router = APIRouter(prefix="/classes", tags=["Classes"])

# === ClassType Routes ===
@router.post("/types", status_code=status.HTTP_201_CREATED)
async def create_class_type_route(request: Request, db_conn = Depends(get_db_connection)):
    try:
        payload = await request.json()
        cursor = db_conn.cursor(dictionary=True)
        result = crud_class.create_class_type(db_conn, cursor, payload)
        db_conn.commit()
        return result
    except HTTPException as e:
        db_conn.rollback()
        raise e
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()

@router.get("/types/{class_type_id}")
def get_class_type_route(class_type_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_class.get_class_type_by_id(db_conn, cursor, class_type_id)

@router.get("/types")
def get_all_class_types_route(db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_class.get_all_class_types(db_conn, cursor)

@router.put("/types/{class_type_id}")
async def update_class_type_route(class_type_id: int, request: Request, db_conn = Depends(get_db_connection)):
    try:
        payload = await request.json()
        cursor = db_conn.cursor(dictionary=True)
        result = crud_class.update_class_type(db_conn, cursor, class_type_id, payload)
        db_conn.commit()
        return result
    except HTTPException as e:
        db_conn.rollback()
        raise e
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()

@router.delete("/types/{class_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class_type_route(class_type_id: int, db_conn = Depends(get_db_connection)):
    try:
        cursor = db_conn.cursor(dictionary=True)
        crud_class.delete_class_type(db_conn, cursor, class_type_id)
        db_conn.commit()
        return None
    except HTTPException as e:
        db_conn.rollback()
        raise e
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()

# === Class Routes ===
@router.get("/")
def get_all_classes_route(detailed: bool = False, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    if detailed:
        return crud_class.get_all_classes_detailed(db_conn, cursor)
    return crud_class.get_all_classes(db_conn, cursor)

@router.get("/{class_id}")
def get_class_route(class_id: int, detailed: bool = False, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    if detailed:
        return crud_class.get_class_detailed_by_id(db_conn, cursor, class_id)
    return crud_class.get_class_by_id(db_conn, cursor, class_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_class_route(request: Request, db_conn = Depends(get_db_connection)):
    try:
        payload = await request.json()
        cursor = db_conn.cursor(dictionary=True)
        result = crud_class.create_class(db_conn, cursor, payload)
        db_conn.commit()
        return result
    except HTTPException as e:
        db_conn.rollback()
        raise e
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()

@router.put("/{class_id}")
async def update_class_route(class_id: int, request: Request, db_conn = Depends(get_db_connection)):
    try:
        payload = await request.json()
        cursor = db_conn.cursor(dictionary=True)
        result = crud_class.update_class(db_conn, cursor, class_id, payload)
        db_conn.commit()
        return result
    except HTTPException as e:
        db_conn.rollback()
        raise e
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()

@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class_route(class_id: int, db_conn = Depends(get_db_connection)):
    try:
        cursor = db_conn.cursor(dictionary=True)
        crud_class.delete_class(db_conn, cursor, class_id)
        db_conn.commit()
        return None
    except HTTPException as e:
        db_conn.rollback()
        raise e
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()

# === ClassBooking Routes ===
@router.post("/bookings", status_code=status.HTTP_201_CREATED)
async def create_class_booking_route(request: Request, db_conn = Depends(get_db_connection)):
    try:
        payload = await request.json()
        cursor = db_conn.cursor(dictionary=True)
        result = crud_class.create_class_booking(db_conn, cursor, payload)
        db_conn.commit()
        return result
    except HTTPException as e:
        db_conn.rollback()
        raise e
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()

@router.get("/bookings/{booking_id}")
def get_class_booking_route(booking_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_class.get_class_booking_by_id(db_conn, cursor, booking_id)

@router.get("/bookings/by-class/{class_id}")
def get_class_bookings_by_class_route(class_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_class.get_class_bookings_by_class_id(db_conn, cursor, class_id)

@router.get("/bookings/by-member/{member_id}")
def get_class_bookings_by_member_route(member_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_class.get_class_bookings_by_member_id(db_conn, cursor, member_id)

@router.put("/bookings/{booking_id}")
async def update_class_booking_route(booking_id: int, request: Request, db_conn = Depends(get_db_connection)):
    try:
        payload = await request.json()
        cursor = db_conn.cursor(dictionary=True)
        result = crud_class.update_class_booking(db_conn, cursor, booking_id, payload)
        db_conn.commit()
        return result
    except HTTPException as e:
        db_conn.rollback()
        raise e
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()

@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class_booking_route(booking_id: int, db_conn = Depends(get_db_connection)):
    try:
        cursor = db_conn.cursor(dictionary=True)
        crud_class.delete_class_booking(db_conn, cursor, booking_id)
        db_conn.commit()
        return None
    except HTTPException as e:
        db_conn.rollback()
        raise e
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()

@router.get("/by-trainer/{trainer_id}")
def get_classes_by_trainer_route(trainer_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_class.get_classes_by_trainer_id(db_conn, cursor, trainer_id)

@router.get("/by-hall/{hall_id}")
def get_classes_by_hall_route(hall_id: int, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_class.get_classes_by_hall_id(db_conn, cursor, hall_id)

@router.get("/by-date-range")
def get_classes_by_date_range_route(start_date: str, end_date: str, db_conn_cursor = Depends(get_db_cursor)):
    db_conn, cursor = db_conn_cursor
    return crud_class.get_classes_by_date_range(db_conn, cursor, start_date, end_date)