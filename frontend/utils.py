# frontend/utils.py (New file)
from typing import Optional
import httpx
from nicegui import ui
import json
from frontend.config import API_HOST, API_PORT

async def api_call(method: str, endpoint: str, payload: Optional[dict] = None, params: Optional[dict] = None) -> Optional[dict]:
    """Helper function to make authenticated API calls."""
    try:
        token = await ui.run_javascript("localStorage.getItem('token')")
        if not token:
            ui.notify("Authentication token not found. Please log in.", color='negative')
            # ui.navigate.to(f"http://{API_HOST}:{API_PORT}/login") # Careful with navigation from non-page context
            return None

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"http://{API_HOST}:{API_PORT}/api{endpoint}" # Assuming /api prefix

        async with httpx.AsyncClient(timeout=10.0) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=payload)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=payload)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers, params=params)
            else:
                ui.notify(f"Unsupported HTTP method: {method}", color='negative')
                return None
        
        if 200 <= response.status_code < 300:
            if response.status_code == 204: # No content
                return {"success": True}
            return response.json()
        else:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get("detail", response.text)
            except: # json.JSONDecodeError
                error_detail = response.text
            ui.notify(f"API Error ({response.status_code}): {error_detail}", color='negative', multi_line=True, close_button='OK')
            return None
            
    except httpx.RequestError as e:
        ui.notify(f"Request failed: {e}", color='negative')
        return None
    except Exception as e:
        ui.notify(f"An unexpected error occurred: {e}", color='negative')
        return None

async def get_current_user_details():
    """Fetches user details from /me endpoint."""
    return await api_call("GET", "/me")