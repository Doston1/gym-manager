# frontend/weekly_schedule.py
from nicegui import ui, app
import httpx
import datetime
import json
import asyncio
from ..config import API_HOST, API_PORT # Assuming your config file

# --- Helper Functions (from your existing code, slightly adapted) ---
async def get_token_from_storage():
    return await ui.run_javascript("localStorage.getItem('token')", timeout=1.0)

async def get_user_info_from_storage():
    user_info_str = await ui.run_javascript("localStorage.getItem('user_info')")
    return json.loads(user_info_str) if user_info_str else None

def is_it_preference_setting_day_local(): # Renamed to avoid conflict if you have a backend check
    """Checks if today (client's local interpretation) is Thursday."""
    return datetime.date.today().weekday() == 3 # Monday is 0, Thursday is 3

def logout_action(): # Renamed to avoid conflict with ui.button if named 'logout'
    ui.run_javascript("localStorage.removeItem('token'); localStorage.removeItem('user_info'); localStorage.removeItem('active_live_session_id');")
    # No need to navigate here if backend /logout redirects properly
    # ui.navigate.to(f"http://{API_HOST}:{API_PORT}/logout") # Backend handles redirect to home
    app.storage.user.clear() # Clear server-side session if you use it
    ui.open(f"http://{API_HOST}:{API_PORT}/logout") # Open in new tab/window to ensure cookie clear for /logout

async def user_has_active_live_session_js(): # Renamed for clarity
    """Checks if active_live_session_id is in localStorage."""
    session_id = await ui.run_javascript("localStorage.getItem('active_live_session_id')")
    return bool(session_id)
# --- End Helper Functions ---

@ui.page('/weekly_schedule')
async def weekly_schedule_page():
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    ui.query('.nicegui-content').classes('items-center')

    current_user = await get_user_info_from_storage()

    # --- Navbar ---
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
        with ui.row().classes('gap-4 items-center'): # Added items-center
            ui.button('Home', on_click=lambda: ui.navigate.to('/')).props('flat text-color=white')
            # Add other common nav buttons here based on your original navbar
            ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).props('flat text-color=white') # Example
            ui.button('Weekly Schedule', on_click=lambda: ui.navigate.to('/weekly_schedule')).props('flat text-color=white')

            if current_user and current_user.get("user_type") == "member" and is_it_preference_setting_day_local():
                 ui.button('Set Preferences', on_click=lambda: ui.navigate.to('/member/set-preferences')).props('flat text-color=white')
            
            if await user_has_active_live_session_js(): # Check if user has an active session
               ui.button('Live Dashboard', on_click=lambda: ui.navigate.to('/live-dashboard')).props('flat text-color=white')


            if current_user:
                user_name = current_user.get("first_name", current_user.get("name", "Account")) # Prefer first_name
                with ui.button(icon='person').props('flat round text-color=white'):
                    with ui.menu().classes('bg-gray-800 text-white'):
                        ui.label(f"Hi, {user_name}!").classes('p-2 text-center')
                        ui.separator()
                        ui.menu_item('My Profile', on_click=lambda: ui.navigate.to('/myprofile'))
                        # Add other user-specific menu items
                        ui.menu_item('Logout', on_click=logout_action)
            else:
                 ui.button('Login', on_click=lambda: ui.open(f'http://{API_HOST}:{API_PORT}/login')).props('flat text-color=white')
    # --- End Navbar ---

    with ui.card().classes('w-full max-w-6xl p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-xl mt-24 mb-8'):
        ui.label('Weekly Training Schedule').classes('text-3xl text-center mb-6 text-blue-300 font-bold')

        # State for the selected week's start date (ISO format string)
        today = datetime.date.today()
        initial_sunday_iso = (today - datetime.timedelta(days=(today.weekday() + 1) % 7)).isoformat()
        selected_week_start_iso = ui.state(initial_sunday_iso)

        with ui.row().classes('w-full items-center justify-between mb-4'):
            def change_week(delta_weeks: int):
                current_start = datetime.date.fromisoformat(selected_week_start_iso.value)
                new_start = current_start + datetime.timedelta(weeks=delta_weeks)
                selected_week_start_iso.value = new_start.isoformat()
                schedule_area.refresh() # Trigger refresh of the schedule display

            ui.button(icon='arrow_back_ios', on_click=lambda: change_week(-1)).props('round flat color=white')
            
            # Display current selected week
            # Using a label that updates reactively with ui.state
            current_week_label = ui.label().classes('text-xl font-semibold')
            def update_week_label(): # Function to update label, will be bound
                 start_dt = datetime.date.fromisoformat(selected_week_start_iso.value)
                 end_dt = start_dt + datetime.timedelta(days=6) # Full week Sun-Sat
                 current_week_label.set_text(f"Week: {start_dt.strftime('%b %d')} - {end_dt.strftime('%b %d, %Y')}")
            
            ui.bind_text_from(selected_week_start_iso, 'value', backward=update_week_label)
            update_week_label() # Initial set

            ui.button(icon='arrow_forward_ios', on_click=lambda: change_week(1)).props('round flat color=white')
            
            if current_user and current_user.get("user_type") == "manager":
                async def handle_generate_schedule():
                    token = await get_token_from_storage()
                    if not token: ui.notify("Not authenticated", type='negative'); return
                    ui.notify(f"Generating schedule for week starting {selected_week_start_iso.value}...", type='ongoing')
                    try:
                        api_url = f"http://{API_HOST}:{API_PORT}/scheduling/weekly-schedules/generate/{selected_week_start_iso.value}"
                        headers = {"Authorization": f"Bearer {token}"}
                        async with httpx.AsyncClient() as client:
                            response = await client.post(api_url, headers=headers)
                        if response.status_code == 200 or response.status_code == 201:
                            ui.notify("Schedule generated successfully! Refreshing...", type='positive')
                            schedule_area.refresh()
                        else:
                            ui.notify(f"Failed to generate schedule: {response.status_code} {response.text}", type='negative')
                    except Exception as e:
                        ui.notify(f"Error generating schedule: {str(e)}", type='negative')

                ui.button('Generate This Week', on_click=handle_generate_schedule).props('color=primary flat')
        
        schedule_area = ui.column().classes('w-full') # Area to be refreshed

        @ui.refreshable
        async def display_schedule_for_week():
            schedule_area.clear() # Clear previous content
            token = await get_token_from_storage()
            if not token or not current_user:
                with schedule_area: ui.label("Please log in to view schedule."); return

            week_to_fetch = selected_week_start_iso.value
            user_type = current_user.get("user_type")
            
            api_url = f"http://{API_HOST}:{API_PORT}/scheduling/weekly-schedules-for-week/{week_to_fetch}"
            params = {}
            headers = {"Authorization": f"Bearer {token}"}

            if user_type == "member":
                member_id = current_user.get("member_id_pk")
                if not member_id: 
                    with schedule_area: ui.label("Member ID not found."); return
                # This uses the more specific endpoint for a member's bookings
                api_url = f"http://{API_HOST}:{API_PORT}/scheduling/members/{member_id}/scheduled-for-week/{week_to_fetch}"
            elif user_type == "trainer":
                trainer_id = current_user.get("trainer_id_pk")
                if not trainer_id: 
                    with schedule_area: ui.label("Trainer ID not found."); return
                params["trainer_id"] = trainer_id
            
            # Manager uses the general URL without specific ID params

            with schedule_area:
                with ui.row().classes('w-full justify-center mb-2'): ui.spinner(size='lg')
                
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(api_url, headers=headers, params=params)
                schedule_area.clear() # Clear spinner

                if response.status_code == 200:
                    sessions_data = response.json()
                    if not sessions_data:
                        with schedule_area: ui.label("No sessions found for this week.").classes('text-center p-4')
                        return

                    # Group by day for display
                    days_in_schedule = sorted(list(set(s['day_of_week'] for s in sessions_data)), key=lambda d: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].index(d))
                    
                    with schedule_area:
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
                                                        session_date_str = f"{datetime.date.fromisoformat(week_to_fetch).year}-{session.get('start_time')}" # This needs fixing
                                                        # We need the full date of the session to compare with today
                                                        # Assuming week_to_fetch is Sunday, and session['day_of_week'] is "Monday", etc.
                                                        days_offset = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].index(session['day_of_week'])
                                                        actual_session_date = datetime.date.fromisoformat(week_to_fetch) + datetime.timedelta(days=days_offset)

                                                        if actual_session_date == datetime.date.today():
                                                            ui.button("Start Live",
                                                                      on_click=lambda s_id=session.get('schedule_id'): handle_start_live_session(s_id)) \
                                                              .props('color=positive flat dense')
                elif response.status_code == 401:
                    with schedule_area: ui.label("Authentication error. Please log in again.")
                    # Consider redirecting to login
                else:
                    with schedule_area: ui.label(f"Failed to load schedule: {response.status_code} - {response.text}")
            except Exception as e:
                schedule_area.clear()
                with schedule_area: ui.label(f"An error occurred: {str(e)}")
                print(f"Error in display_schedule_for_week: {e}")

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
                    await ui.run_javascript(f"localStorage.setItem('active_live_session_id', '{live_session_id}');")
                    ui.notify("Live session started! Redirecting...", type='positive')
                    ui.navigate.to('/live-dashboard') # Navigate to the live dashboard page
                else:
                    ui.notify(f"Failed to start live session: {response.status_code} - {response.text}", type='negative')
            except Exception as e:
                ui.notify(f"Error starting live session: {str(e)}", type='negative')

        # Trigger initial display and allow refresh
        display_schedule_for_week() # Call it directly as it's now refreshable container

    # ui.timer(300, load_schedule) # Example: Refresh every 5 minutes - careful with this