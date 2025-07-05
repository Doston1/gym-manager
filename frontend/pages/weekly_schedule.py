# frontend/weekly_schedule.py
from nicegui import ui, app
import httpx
import datetime
import json
import asyncio
from ..config import API_HOST, API_PORT
from frontend.components.navbar import create_navbar_with_conditional_buttons, apply_page_style, get_current_user

# --- Helper Functions (from your existing code, slightly adapted) ---
async def get_token_from_storage():
    return await ui.run_javascript("localStorage.getItem('token')", timeout=1.0)

async def get_user_info_from_storage():
    user_info_str = await ui.run_javascript("localStorage.getItem('user_info')", timeout=5.0)
    return json.loads(user_info_str) if user_info_str else None

def is_it_preference_setting_day_local(): # Renamed to avoid conflict if you have a backend check
    """Checks if today (client's local interpretation) is Thursday."""
    return datetime.date.today().weekday() == 3 # Monday is 0, Thursday is 3

async def user_has_active_live_session_js(): # Renamed for clarity
    """Checks if active_live_session_id is in localStorage."""
    session_id = await ui.run_javascript("localStorage.getItem('active_live_session_id')", timeout=5.0)
    return bool(session_id)
# --- End Helper Functions ---

@ui.page('/weekly_schedule')
async def weekly_schedule_page():
    # Apply consistent page styling
    apply_page_style()
    ui.query('.nicegui-content').classes('items-center')
    
    current_user = await get_user_info_from_storage()

    # Define conditional buttons for the navbar
    conditional_buttons = []
    
    # Add Set Preferences button if user is member and it's Thursday
    if current_user and current_user.get("user_type") == "member" and is_it_preference_setting_day_local():
        conditional_buttons.append({
            'condition_func': lambda: True,  # Already checked the condition above
            'label': 'Set Preferences',
            'on_click': lambda: ui.navigate.to('/member/set-preferences'),
            'classes': 'text-white hover:text-blue-300'
        })
    
    # Add Live Dashboard button if user has active session
    if await user_has_active_live_session_js():
        conditional_buttons.append({
            'condition_func': lambda: True,  # Already checked the condition above
            'label': 'Live Dashboard',
            'on_click': lambda: ui.navigate.to('/live-dashboard'),
            'classes': 'text-white hover:text-blue-300'
        })

    # Additional standard buttons
    additional_buttons = [
        {
            'label': 'Weekly Schedule',
            'on_click': lambda: ui.navigate.to('/weekly_schedule'),
            'classes': 'text-white hover:text-blue-300'
        }
    ]

    # Create navbar with conditional buttons
    user = await create_navbar_with_conditional_buttons(check_functions=conditional_buttons)

    with ui.card().classes('w-full max-w-6xl mx-auto p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-xl mt-24 mb-8'): # Added mx-auto for centering
        ui.label('Weekly Training Schedule').classes('text-3xl text-center mb-6 text-blue-300 font-bold')

        # State for the selected week's start date (ISO format string)
        today = datetime.date.today()
        initial_sunday_iso = (today - datetime.timedelta(days=(today.weekday() + 1) % 7)).isoformat()
        
        # Use a container for the schedule content that can be refreshed
        schedule_container = ui.column().classes('w-full')
        
        # Current week state - using a simple approach
        current_week_start = {'value': initial_sunday_iso}

        with ui.row().classes('w-full items-center justify-between mb-4'):
            def change_week(delta_weeks: int):
                current_start = datetime.date.fromisoformat(current_week_start['value'])
                new_start = current_start + datetime.timedelta(weeks=delta_weeks)
                current_week_start['value'] = new_start.isoformat()
                update_week_label()
                # Clear and refresh the schedule container
                schedule_container.clear()
                ui.timer(0.1, lambda: refresh_schedule_async(current_week_start['value'], current_user, schedule_container), once=True)

            ui.button(icon='arrow_back_ios', on_click=lambda: change_week(-1)).props('round flat color=white')
            
            # Display current selected week
            current_week_label = ui.label().classes('text-xl font-semibold')
            def update_week_label():
                 start_dt = datetime.date.fromisoformat(current_week_start['value'])
                 end_dt = start_dt + datetime.timedelta(days=6) # Full week Sun-Sat
                 current_week_label.set_text(f"Week: {start_dt.strftime('%b %d')} - {end_dt.strftime('%b %d, %Y')}")
            
            update_week_label() # Initial set

            ui.button(icon='arrow_forward_ios', on_click=lambda: change_week(1)).props('round flat color=white')
            
            if current_user and current_user.get("user_type") == "manager":
                async def handle_generate_schedule():
                    token = await get_token_from_storage()
                    if not token: ui.notify("Not authenticated", type='negative'); return
                    ui.notify(f"Generating schedule for week starting {current_week_start['value']}...", type='ongoing')
                    try:
                        api_url = f"http://{API_HOST}:{API_PORT}/scheduling/weekly-schedules/generate/{current_week_start['value']}"
                        headers = {"Authorization": f"Bearer {token}"}
                        async with httpx.AsyncClient() as client:
                            response = await client.post(api_url, headers=headers)
                        if response.status_code == 200 or response.status_code == 201:
                            ui.notify("Schedule generated successfully! Refreshing...", type='positive')
                            ui.timer(0.1, lambda: refresh_schedule_async(current_week_start['value'], current_user, schedule_container), once=True)
                        else:
                            ui.notify(f"Failed to generate schedule: {response.status_code} {response.text}", type='negative')
                    except Exception as e:
                        ui.notify(f"Error generating schedule: {str(e)}", type='negative')

                ui.button('Generate This Week', on_click=handle_generate_schedule).props('color=primary flat')
        
        # Initial load of the schedule
        ui.timer(0.1, lambda: refresh_schedule_async(current_week_start['value'], current_user, schedule_container), once=True)

async def refresh_schedule_async(week_start_iso: str, current_user, container):
    """Helper function to refresh schedule content asynchronously"""
    container.clear()
    with container:
        await create_schedule_content(week_start_iso, current_user)

async def create_schedule_content(week_start_iso: str, current_user):
    """Create the schedule content for a given week"""
    token = await get_token_from_storage()
    if not token or not current_user:
        ui.label("Please log in to view schedule.")
        return

    user_type = current_user.get("user_type")
    
    api_url = f"http://{API_HOST}:{API_PORT}/scheduling/weekly-schedules-for-week/{week_start_iso}"
    params = {}
    headers = {"Authorization": f"Bearer {token}"}

    if user_type == "member":
        member_id = current_user.get("member_id_pk")
        if not member_id: 
            ui.label("Member ID not found.")
            return
        # This uses the more specific endpoint for a member's bookings
        api_url = f"http://{API_HOST}:{API_PORT}/scheduling/members/{member_id}/scheduled-for-week/{week_start_iso}"
    elif user_type == "trainer":
        trainer_id = current_user.get("trainer_id_pk")
        if not trainer_id: 
            ui.label("Trainer ID not found.")
            return
        params["trainer_id"] = trainer_id
    
    # Manager uses the general URL without specific ID params

    with ui.row().classes('w-full justify-center mb-2'): 
        ui.spinner(size='lg')
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers, params=params)

        if response.status_code == 200:
            sessions_data = response.json()
            if not sessions_data:
                ui.label("No sessions found for this week.").classes('text-center p-4')
                return

            # Group by day for display
            days_in_schedule = sorted(list(set(s['day_of_week'] for s in sessions_data)), key=lambda d: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].index(d))
            
            with ui.tabs().classes('w-full') as tabs:
                for day_name in days_in_schedule:
                    ui.tab(day_name)
            with ui.tab_panels(tabs, value=days_in_schedule[0]).props('animated').classes('w-full bg-transparent'):
                for day_name in days_in_schedule:
                    with ui.tab_panel(day_name):
                        day_sessions = sorted([s for s in sessions_data if s['day_of_week'] == day_name], key=lambda x: x['start_time'])
                        if not day_sessions:
                            ui.label(f"No sessions on {day_name}.").classes('p-4 text-center')
                            continue
                        
                        for session in day_sessions:
                            card_color = "bg-gray-800" # Default
                            if session.get('status') == 'Completed': card_color = "bg-green-900"
                            elif session.get('status') == 'Cancelled': card_color = "bg-red-900"
                            elif session.get('status') == 'In Progress': card_color = "bg-blue-800"

                            with ui.card().classes(f'w-full my-2 {card_color} text-white rounded-lg shadow-md'):
                                session_title = ""
                                if user_type == "member":
                                    session_title = session.get("plan_day_name") or session.get("class_type_name", "Your Training")
                                elif user_type == "trainer" or user_type == "manager":
                                    # For trainer/manager, you might want to show class type or if it's PT
                                    # The API for weekly-schedules-for-week (get_by_week in SQL) provides hall_name, trainer_name
                                    # For member view, it's from schedule_members_get_by_member_id_and_week
                                    session_title = session.get("class_type_name", f"Session with {session.get('trainer_name', 'Trainer')}") if 'class_type_name' in session else f"Session for Trainer: {session.get('trainer_name', 'N/A')}"


                                with ui.expansion(f"{session.get('start_time','')} - {session.get('end_time','')} | {session_title}", icon='event').classes('w-full'):
                                    ui.separator()
                                    with ui.card_section():
                                        ui.label(f"Hall: {session.get('hall_name', 'N/A')}")
                                        if user_type != "trainer": # Member and Manager see trainer
                                            ui.label(f"Trainer: {session.get('trainer_name', 'N/A')}")
                                        if user_type == "trainer" or user_type == "manager":
                                            ui.label(f"Capacity: {session.get('current_participants',0)}/{session.get('max_capacity','N/A')}")
                                            ui.label(f"Status: {session.get('status', 'N/A')}")
                                        
                                        # "Start Live Session" button (logic from your original code, adapted)
                                        if (user_type == "trainer" or user_type == "manager") and session.get("status") == "Scheduled":
                                            # Check if session is today
                                            # We need the full date of the session to compare with today
                                            # Assuming week_start_iso is Sunday, and session['day_of_week'] is "Monday", etc.
                                            days_offset = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].index(session['day_of_week'])
                                            actual_session_date = datetime.date.fromisoformat(week_start_iso) + datetime.timedelta(days=days_offset)

                                            if actual_session_date == datetime.date.today():
                                                ui.button("Start Live",
                                                          on_click=lambda s_id=session.get('schedule_id'): handle_start_live_session(s_id)) \
                                                  .props('color=positive flat dense')
        elif response.status_code == 401:
            ui.label("Authentication error. Please log in again.")
            # Consider redirecting to login
        else:
            ui.label(f"Failed to load schedule: {response.status_code} - {response.text}")
    except Exception as e:
        ui.label(f"An error occurred: {str(e)}")
        print(f"Error in create_schedule_content: {e}")

async def handle_start_live_session(schedule_id: int):
    if not schedule_id: return
    token = await get_token_from_storage()
    if not token: ui.notify("Not authenticated.", type='negative'); return

    ui.notify(f"Starting live session for schedule ID {schedule_id}...", type='ongoing')
    try:
        api_url = f"http://{API_HOST}:{API_PORT}/training-execution/live-sessions/start"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {"schedule_id": schedule_id}
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 201: # Assuming 201 Created for new live session
            live_session_data = response.json()
            live_session_id = live_session_data.get("live_session_id")
            await ui.run_javascript(f"localStorage.setItem('active_live_session_id', '{live_session_id}');", timeout=5.0)
            ui.notify("Live session started! Redirecting...", type='positive')
            ui.navigate.to('/live-dashboard') # Navigate to the live dashboard page
        else:
            ui.notify(f"Failed to start live session: {response.status_code} - {response.text}", type='negative')
    except Exception as e:
        ui.notify(f"Error starting live session: {str(e)}", type='negative')