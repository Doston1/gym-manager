# frontend/member_preferences.py
from nicegui import ui, app
from datetime import time, date, timedelta, datetime
import httpx # For API calls
import json
from ..config import API_HOST, API_PORT
from frontend.components.navbar import create_navbar, apply_page_style, get_current_user

# --- Helper to get token (consistent with your weekly_schedule.py) ---
async def get_token_from_storage():
    return await ui.run_javascript("localStorage.getItem('token')", timeout=1.0)

# Define preference options and colors
PREFERENCE_OPTIONS_MAP = {
    "Available": {"color": "green-6", "text": "Available", "value": "Available"},
    "PreferredNot": {"color": "blue-6", "text": "Can, prefer not", "value": "PreferredNot"}, # Value for backend
    "NotAvailable": {"color": "red-6", "text": "Can't", "value": "NotAvailable"},
}
# Order matters for cycling
PREFERENCE_CYCLE_ORDER = ["Available", "PreferredNot", "NotAvailable"]

TIME_SLOTS = [ # Using tuples for start/end as strings for direct API use
    ("08:00:00", "10:00:00"), ("10:00:00", "12:00:00"),
    ("12:00:00", "14:00:00"), ("14:00:00", "16:00:00"),
    ("16:00:00", "18:00:00"), ("18:00:00", "20:00:00"),
]
DAYS_OF_WEEK_FOR_PREFERENCES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

def get_next_week_sunday_iso():
    today = date.today()
    current_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
    return (current_sunday + timedelta(days=7)).isoformat()

@ui.page('/member/set-preferences')
async def member_set_preferences_page():
    # Apply consistent page styling
    apply_page_style()

    # Create navbar and get user
    user = await create_navbar()
    
    if not user or user.get("user_type") != "member":
        with ui.card().classes('w-full max-w-md p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-20'):
            ui.label("Access Denied. This page is for members only.").classes('text-center text-red-400')
            ui.button("Go Home", on_click=lambda: ui.navigate.to('/')).classes('w-full mt-4')
        return
    
    member_id = user.get("member_id_pk") # Assuming your /me endpoint returns this
    if not member_id:
        ui.notify("Error: Member ID not found in your session.", type='negative')
        return

    with ui.card().classes('w-full max-w-4xl p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-20'):
        ui.label("Set Your Training Preferences").classes('text-2xl font-semibold mb-1 text-center text-blue-300')
        
        next_week_sunday_iso = get_next_week_sunday_iso()
        next_week_sunday_dt = date.fromisoformat(next_week_sunday_iso)
        next_week_thursday_dt = next_week_sunday_dt + timedelta(days=4)
        
        ui.label(f"For week: {next_week_sunday_dt.strftime('%A, %b %d')} to {next_week_thursday_dt.strftime('%A, %b %d')}").classes('text-lg mb-4 text-center')

        preferences_state = {} # Key: (day_name, start_time_str, end_time_str), Value: preference_value_from_map

        async def load_preferences_from_api():
            nonlocal preferences_state
            preferences_state.clear()
            token = await get_token_from_storage()
            if not token:
                ui.notify("Authentication token not found.", type='negative')
                return

            try:
                # Assuming your backend /scheduling/members/{member_id}/preferences-for-week?week_start_date=YYYY-MM-DD
                # If your /me provides member_id, you might not need it in URL if backend uses authenticated user
                api_url = f"http://{API_HOST}:{API_PORT}/scheduling/members/{member_id}/preferences-for-week"
                headers = {"Authorization": f"Bearer {token}"}
                params = {"week_start_date": next_week_sunday_iso}
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(api_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    loaded_prefs = response.json()
                    for pref in loaded_prefs: # Assuming API returns a list of preference objects
                        key = (pref["day_of_week"], pref["start_time"], pref["end_time"])
                        preferences_state[key] = pref["preference_type"] # e.g., "Available", "NotAvailable"
                elif response.status_code == 404: # No preferences set yet for this week
                    pass # preferences_state remains empty, which is fine
                else:
                    ui.notify(f"Could not load existing preferences: {response.status_code} {response.text}", type='warning')
            except Exception as e:
                ui.notify(f"Error loading preferences: {str(e)}", type='negative')
            preferences_grid.refresh()

        @ui.refreshable
        def preferences_grid():
            with ui.grid(columns=len(TIME_SLOTS) + 1).classes('gap-1 w-full mt-4'):
                ui.label() # Top-left empty
                for start_str, end_str in TIME_SLOTS:
                    ui.label(f"{start_str[:5]}-{end_str[:5]}").classes('text-center font-medium text-sm')

                for day_idx, day_name in enumerate(DAYS_OF_WEEK_FOR_PREFERENCES):
                    current_slot_date = next_week_sunday_dt + timedelta(days=day_idx)
                    ui.label(f"{day_name}\n{current_slot_date.strftime('%d')}") \
                        .classes('text-center font-medium py-2 whitespace-pre-line text-sm')
                    
                    for start_str, end_str in TIME_SLOTS:
                        slot_key = (day_name, start_str, end_str)
                        current_pref_value = preferences_state.get(slot_key, PREFERENCE_CYCLE_ORDER[0]) # Default to "Available"
                        
                        current_pref_details = PREFERENCE_OPTIONS_MAP.get(current_pref_value, {"color":"gray-5", "text":"Set"})

                        def create_handler(s_key, current_val):
                            async def on_click():
                                current_idx = PREFERENCE_CYCLE_ORDER.index(current_val)
                                next_idx = (current_idx + 1) % len(PREFERENCE_CYCLE_ORDER)
                                preferences_state[s_key] = PREFERENCE_CYCLE_ORDER[next_idx]
                                preferences_grid.refresh()
                            return on_click

                        ui.button(current_pref_details["text"],
                                  on_click=create_handler(slot_key, current_pref_value),
                                  color=current_pref_details["color"]) \
                          .props('flat size=sm').classes('w-full h-12 text-xs')
        
        await load_preferences_from_api() # Initial load
        preferences_grid()

        async def handle_save_all_preferences():
            token = await get_token_from_storage()
            if not token:
                ui.notify("Authentication token not found. Cannot save.", type='negative')
                return

            ui.notify("Saving preferences...", type='ongoing')
            payloads_to_send = []
            for (day, start_t, end_t), pref_type in preferences_state.items():
                payloads_to_send.append({
                    "member_id": member_id, # Backend might ignore this if using authenticated user
                    "week_start_date": next_week_sunday_iso,
                    "day_of_week": day,
                    "start_time": start_t,
                    "end_time": end_t,
                    "preference_type": pref_type,
                })
            
            if not payloads_to_send:
                ui.notify("No preferences set to save.", type='info')
                return

            try:
                # This assumes your backend /scheduling/preferences/batch endpoint can handle a list of preference objects
                # and will perform upserts.
                api_url = f"http://{API_HOST}:{API_PORT}/scheduling/preferences/batch" # YOU NEED TO CREATE THIS BATCH ENDPOINT
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(api_url, headers=headers, content=json.dumps(payloads_to_send))
                
                if response.status_code == 200 or response.status_code == 201:
                    ui.notify("Preferences saved successfully!", type='positive')
                    await load_preferences_from_api() # Refresh from server
                else:
                    ui.notify(f"Error saving preferences: {response.status_code} - {response.text}", type='negative')
            except Exception as e:
                ui.notify(f"Failed to save preferences: {str(e)}", type='negative')

        with ui.row().classes('w-full justify-center mt-6 gap-4'):
            ui.button("Save All Preferences", on_click=handle_save_all_preferences).props('color=primary')
            ui.button("Back to Schedule", on_click=lambda: ui.navigate.to('/weekly_schedule')).props('color=grey')