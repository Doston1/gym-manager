from typing import Dict

# In-memory session storage (Replace with Redis for production)
user_sessions: Dict[str, dict] = {}

def get_user_session(user_id: str):
    """Retrieve user session details."""
    print("DEBUG:session.py, user_sessions:", user_sessions)
    return user_sessions.get(user_id)

def set_user_session(user_id: str, user_info: dict):
    """Save user session details."""
    user_sessions[user_id] = user_info

def remove_user_session(user_id: str):
    """Remove user session on logout."""
    user_sessions.pop(user_id, None)

def is_user_logged_in(user_id: str) -> bool:
    """Check if the user is logged in."""
    return user_id in user_sessions
