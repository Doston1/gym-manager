import os
import re # For parsing named queries
from datetime import date, datetime, time
from decimal import Decimal

_SQL_QUERIES = {}
_SQL_DIR = os.path.join(os.path.dirname(__file__), "sql_queries")

def _load_queries_from_dir(directory):
    if not os.path.exists(directory):
        print(f"Warning: SQL queries directory not found: {directory}")
        return
    
    _SQL_QUERIES.clear() # Clear existing queries before reloading

    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".sql"):
                # entity_name is derived from filename, e.g., "users" from "users.sql"
                # This will be the prefix for the query keys from this file.
                entity_prefix = os.path.splitext(file_name)[0] 
                
                # If you have subdirectories in sql_queries, you might want to include them in the prefix
                # For example, if you have sql_queries/auth/user_queries.sql
                # relative_path = os.path.relpath(root, _SQL_DIR)
                # if relative_path and relative_path != ".":
                #     entity_prefix = f"{relative_path.replace(os.sep, '_')}_{entity_prefix}"

                file_path = os.path.join(root, file_name)
                
                with open(file_path, "r") as f:
                    content = f.read()
                
                # Regex to find "-- NAME: query_name" (case-insensitive for NAME)
                # and the SQL that follows until the next -- NAME: or end of file.
                # Captures: 1=query_name_in_file, 2=query_sql
                query_blocks = re.findall(
                    r"--\s*NAME:\s*([a-zA-Z0-9_]+)\s*\n(.*?)(?=(?:--\s*NAME:|$))", 
                    content, 
                    re.DOTALL | re.IGNORECASE
                )

                if query_blocks:
                    for query_name_in_file, query_sql in query_blocks:
                        # Construct the full key, e.g., "users_get_by_auth_id"
                        full_key = f"{entity_prefix}_{query_name_in_file.lower()}"
                        _SQL_QUERIES[full_key] = query_sql.strip()
                elif content.strip() and not query_blocks: # File has content but no valid -- NAME: tags
                    print(f"Warning: File '{file_name}' in '{root}' contains SQL but no '-- NAME:' tags or tags are improperly formatted. Queries from this file not loaded with specific names.")

def get_sql(query_key: str) -> str:
    # Normalize query_key to lowercase to match how keys are stored if needed,
    # but full_key is already lowercased for the query_name_in_file part.
    # Let's assume query_key is passed as expected (e.g., "users_get_by_auth_id")
    
    # if not _SQL_QUERIES: # Initial load if empty
    #     _load_queries_from_dir(_SQL_DIR)
    # The above line can cause issues if called from multiple threads at startup.
    # Better to ensure _load_queries_from_dir is called once when the module loads.

    query = _SQL_QUERIES.get(query_key) # query_key directly
    
    if query is None:
        # Attempt a reload in case files were added/changed after initial app start (useful for dev)
        print(f"Query key '{query_key}' not found, attempting to reload queries...")
        _load_queries_from_dir(_SQL_DIR) # This will clear and reload all queries
        query = _SQL_QUERIES.get(query_key)
        if query is None:
            raise ValueError(f"SQL query with key '{query_key}' not found even after reload. Loaded keys: {list(_SQL_QUERIES.keys())}")
    return query

# Initial load of queries when this module is first imported
_load_queries_from_dir(_SQL_DIR)


# --- Helper functions for data formatting and validation ---
def format_datetime_fields(row):
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
            row[key] = float(value)
        elif isinstance(value, bytes):
            row[key] = value.decode('utf-8')
    return row

def format_records(records):
    if isinstance(records, list):
        return [format_datetime_fields(row) for row in records]
    return format_datetime_fields(records)

def validate_payload(payload: dict, required_fields: list, optional_fields: list = None):
    if optional_fields is None:
        optional_fields = []
    payload_keys = set(payload.keys())
    all_allowed_fields = set(required_fields + optional_fields)
    for field in required_fields:
        if field not in payload: # or payload[field] is None: (check if None is permissible for required fields)
            raise ValueError(f"Missing required field: {field}")
    unknown_fields = payload_keys - all_allowed_fields
    if unknown_fields:
        raise ValueError(f"Unknown fields in payload: {', '.join(unknown_fields)}")
    return {k: v for k, v in payload.items() if k in all_allowed_fields and v is not None} # Filter out None values from payload

if __name__ == "__main__":
    print("Attempting to load queries...")
    # _load_queries_from_dir(_SQL_DIR) # Already called on module load
    print("Loaded SQL Keys (on module load):", list(_SQL_QUERIES.keys()))
    try:
        print("\nFetching 'users_get_by_auth_id':") # Example key
        print(get_sql("users_get_by_auth_id"))
    except ValueError as e:
        print(e)
    try:
        print("\nFetching 'another_example_key_if_exists':") # Example key
        print(get_sql("halls_get_all")) # Change to an actual key you expect
    except ValueError as e:
        print(e)