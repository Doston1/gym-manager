import os
from datetime import date, datetime, time
from decimal import Decimal

_SQL_QUERIES = {}
_SQL_DIR = os.path.join(os.path.dirname(__file__), "sql_queries")

def _load_queries_from_dir(directory):
    if not os.path.exists(directory):
        print(f"Warning: SQL queries directory not found: {directory}")
        return
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".sql"):
                query_name = os.path.splitext(file_name)[0]
                relative_path = os.path.relpath(root, _SQL_DIR)
                
                # Normalize path for key construction
                key_prefix_parts = [part for part in relative_path.split(os.sep) if part and part != "."]
                key_prefix = "_".join(key_prefix_parts)
                
                if key_prefix:
                    full_key = f"{key_prefix}_{query_name}"
                else:
                    full_key = query_name
                
                with open(os.path.join(root, file_name), "r") as f:
                    _SQL_QUERIES[full_key] = f.read().strip()

def get_sql(query_key: str) -> str:
    if not _SQL_QUERIES: # Load on first call if not already loaded
        _load_queries_from_dir(_SQL_DIR)
    
    query = _SQL_QUERIES.get(query_key)
    if query is None:
        # Try reloading if not found, in case files were added after initial load
        _load_queries_from_dir(_SQL_DIR)
        query = _SQL_QUERIES.get(query_key)
        if query is None:
            raise ValueError(f"SQL query with key '{query_key}' not found. Loaded keys: {list(_SQL_QUERIES.keys())}")
    return query

# Initial load of queries
_load_queries_from_dir(_SQL_DIR)


def format_datetime_fields(row):
    """Converts datetime, date, time objects in a dictionary to ISO strings."""
    if row is None:
        return None
    for key, value in row.items():
        if isinstance(value, datetime):
            row[key] = value.isoformat()
        elif isinstance(value, date):
            row[key] = value.isoformat()
        elif isinstance(value, time):
            row[key] = value.isoformat()
        elif isinstance(value, Decimal):
            row[key] = float(value) # Convert Decimal to float for JSON
        elif isinstance(value, bytes): # Handle ENUMs if they come as bytes
            row[key] = value.decode('utf-8')
    return row

def format_records(records):
    """Formats a list of records or a single record."""
    if isinstance(records, list):
        return [format_datetime_fields(row) for row in records]
    return format_datetime_fields(records)

def validate_payload(payload: dict, required_fields: list, optional_fields: list = None):
    """
    Validates if required fields are present in the payload.
    Checks if only required or optional fields are present.
    """
    if optional_fields is None:
        optional_fields = []

    payload_keys = set(payload.keys())
    all_allowed_fields = set(required_fields + optional_fields)

    # Check for missing required fields
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")
        # Optionally, check if the field is empty if it's not allowed to be
        # if payload[field] is None or str(payload[field]).strip() == "":
        #     raise ValueError(f"Required field '{field}' cannot be empty")


    # Check for unknown fields
    unknown_fields = payload_keys - all_allowed_fields
    if unknown_fields:
        raise ValueError(f"Unknown fields in payload: {', '.join(unknown_fields)}")

    return {k: v for k, v in payload.items() if k in all_allowed_fields and v is not None}