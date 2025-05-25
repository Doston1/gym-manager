from nicegui import ui
import datetime
from frontend.config import API_HOST, API_PORT
from frontend.utils import api_call, get_current_user_details
import asyncio

async def display_weekly_schedule():
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    ui.query('.nicegui-content').classes('items-center')

    user = await get_current_user_details()
    if not user:
        ui.label("Please log in to view the schedule.").classes('text-xl m-auto')
        ui.button("Login", on_click=lambda: ui.navigate.to(f"http://{API_HOST}:{API_PORT}/login"))
        return

    # --- Navbar ---
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold').on('click', lambda: ui.navigate.to('/'))
        # ... (add other nav buttons from home_page.py) ...

    # --- Main Content ---
    with ui.card().classes('w-full max-w-6xl p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-4'):
        ui.label('Weekly Training Schedule').classes('text-3xl font-bold text-center mb-6 text-blue-300')

        schedule_display_area = ui.column().classes('w-full')

        # Week selection
        today = datetime.date.today()
        current_week_start_offset = (today.weekday() - 6) % 7 # Monday=0, Sunday=6 -> make Sunday=0
        current_week_start = today - datetime.timedelta(days=current_week_start_offset)
        next_week_start = current_week_start + datetime.timedelta(weeks=1)

        week_options = {
            f"Current Week ({current_week_start.isoformat()})": current_week_start.isoformat(),
            f"Next Week ({next_week_start.isoformat()})": next_week_start.isoformat(),
        }
        
        selected_week_iso = ui.state(current_week_start.isoformat())

        with ui.row().classes("w-full items-center justify-between mb-4"):
            ui.select(week_options, label="Select Week", value=f"Current Week ({current_week_start.isoformat()})",
                      on_change=lambda e: setattr(selected_week_iso, 'value', week_options[e.value]) or load_schedule_for_week()).classes("w-64")

            if user.get("user_type") == "manager" and datetime.date.today().weekday() >= 4: # Friday or later
                 # For simplicity, manager can always try to generate/regenerate
                 # The backend scheduler.py handles the actual timing logic (Fri/Sat)
                 # Here, this button could trigger an ad-hoc regeneration if needed or just be illustrative
                 pass # The actual scheduling is by APScheduler. Manual trigger could be added.


        async def load_schedule_for_week():
            schedule_display_area.clear()
            week_to_load = selected_week_iso.value
            endpoint_suffix = ""
            if user.get("user_type") == "member":
                endpoint_suffix = f"/member/{week_to_load}"
            elif user.get("user_type") == "trainer":
                endpoint_suffix = f"/trainer/{week_to_load}"
            elif user.get("user_type") == "manager":
                endpoint_suffix = f"/manager/{week_to_load}"
            
            if not endpoint_suffix:
                with schedule_display_area: ui.label("Invalid user type for schedule viewing.")
                return

            schedule_data = await api_call("GET", f"/weekly-schedule{endpoint_suffix}")

            with schedule_display_area:
                if not schedule_data:
                    ui.label(f"No schedule found for the week of {week_to_load} for your role.").classes("text-lg text-center")
                    return

                days_in_schedule = sorted(list(set(item['day_of_week'] for item in schedule_data)), key=lambda d: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].index(d))
                
                with ui.tabs().classes('w-full') as tabs:
                    for day_name in days_in_schedule:
                        ui.tab(day_name)
                
                with ui.tab_panels(tabs, value=days_in_schedule[0] if days_in_schedule else None).classes('w-full'):
                    for day_name in days_in_schedule:
                        with ui.tab_panel(day_name):
                            day_sessions = [s for s in schedule_data if s['day_of_week'] == day_name]
                            day_sessions.sort(key=lambda s: s['start_time'])

                            if not day_sessions:
                                ui.label(f"No sessions scheduled for {day_name}.").classes("text-info")
                                continue

                            for session in day_sessions:
                                with ui.card().classes("w-full p-3 my-2 bg-gray-800"):
                                    ui.label(f"{session['start_time']} - {session['end_time']}").classes("text-xl font-semibold")
                                    ui.label(f"Hall: {session.get('hall_name', session.get('hall_id'))}") # Adapt based on response
                                    ui.label(f"Trainer: {session.get('trainer_name', session.get('trainer_id'))}")
                                    
                                    if user.get("user_type") == "member":
                                        # Display member's status for this session
                                        member_in_session = next((sm for sm in session.get('schedule_members', []) if sm['member_id'] == user.get('member_id')), None)
                                        if member_in_session:
                                            ui.label(f"Your Status: {member_in_session['status']}")
                                            # Add cancel/change buttons if within window (Fri-Sat 00:00)
                                            # publication_date = datetime.datetime.strptime(week_to_load, '%Y-%m-%d').date() - datetime.timedelta(days=2) # Assuming schedule published on Friday
                                            # if publication_date <= datetime.date.today() < publication_date + datetime.timedelta(days=1) \
                                            #    and member_in_session['status'] not in ['Cancelled', 'Attended', 'No Show']:
                                            #    ui.button("Cancel Training", on_click=lambda s_id=member_in_session['id']: cancel_my_training(s_id)).props("color=negative dense")
                                    
                                    elif user.get("user_type") in ["trainer", "manager"]:
                                        ui.label(f"Capacity: {len(session.get('schedule_members',[]))} / {session['max_capacity']}")
                                        with ui.expansion("View Members"):
                                            members_in_session = session.get('schedule_members', [])
                                            if members_in_session:
                                                for sm_detail in members_in_session:
                                                    # Need member names here - backend should provide
                                                    ui.label(f"Member ID: {sm_detail['member_id']} - Status: {sm_detail['status']}")
                                            else:
                                                ui.label("No members assigned yet.")
        
        async def cancel_my_training(schedule_member_id):
            # Ensure it's within the 24-hour cancellation window after schedule publication (Friday X to Saturday X)
            # For simplicity, check if it's Friday or Saturday morning before the final reschedule.
            today = datetime.date.today()
            # This logic needs refinement based on exact publication time and deadline.
            # if not (today.weekday() == 4 or (today.weekday() == 5 and datetime.datetime.now().hour < 0)): # Friday, or Sat before midnight
            #     ui.notify("Cancellation/change window is closed.", color='warning')
            #     return

            result = await api_call("PUT", f"/weekly-schedule/member/{schedule_member_id}/status?new_status=Cancelled")
            if result:
                ui.notify("Training cancelled successfully.", color='positive')
                await load_schedule_for_week()
            else:
                ui.notify("Failed to cancel training.", color='negative')

        await load_schedule_for_week()



# ============ OLDER VERSION ==============
# from nicegui import ui, app # Added app import
# import requests
# import datetime
# import json
# import asyncio
# from ..config import API_HOST, API_PORT
# import httpx # Added httpx import

# # --- Copied Helper Functions ---
# async def get_current_user():
#     try:
#         token = await ui.run_javascript(
#             "localStorage.getItem('token')",
#             timeout=5.0
#         )
#         if token:
#             headers = {"Authorization": f"Bearer {token}"}
#             async with httpx.AsyncClient() as client:
#                 response = await client.get(f"http://{API_HOST}:{API_PORT}/me", headers=headers)
#             if response.status_code == 200:
#                 user_data = response.json()
#                 await ui.run_javascript(f"localStorage.setItem('user_info', '{json.dumps(user_data)}');")
#                 return user_data
#     except Exception as e:
#         print(f"Error getting current user: {e}")
#     return None

# def logout():
#     ui.run_javascript("localStorage.removeItem('token'); localStorage.removeItem('user_info'); location.reload();")
#     ui.navigate.to(f"http://{API_HOST}:{API_PORT}/logout")

# async def is_preference_day():
#     # Simple check for Thursday (weekday 3)
#     return datetime.date.today().weekday() == 3

# # Placeholder for checking active session - Requires Backend Implementation
# async def user_has_active_session(user):
#     if not user:
#         return False
#     try:
#         token = await ui.run_javascript("localStorage.getItem('token')")
#         if not token:
#             return False
#         headers = {"Authorization": f"Bearer {token}"}
#         async with httpx.AsyncClient() as client:
#             # Replace with the actual endpoint once created
#             response = await client.get(f"http://{API_HOST}:{API_PORT}/training/live/sessions/current", headers=headers)
#             if response.status_code == 200 and response.json(): # Check if response is OK and has content
#                 # Store active session ID if needed
#                 # await ui.run_javascript(f"localStorage.setItem('active_live_session_id', '{response.json().get('live_session_id')}');")
#                 return True
#             # Handle cases where session is not active or error occurs
#             # await ui.run_javascript("localStorage.removeItem('active_live_session_id');")
#             return False
#     except Exception as e:
#         print(f"Error checking active session: {e}")
#         # await ui.run_javascript("localStorage.removeItem('active_live_session_id');")
#         return False

# # --- End Copied Helper Functions ---

# async def display_weekly_schedule(): # Made async
#     # Apply background style
#     ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
#     ui.query('.nicegui-content').classes('items-center')

#     user = await get_current_user()

#     # --- Copied Navbar ---
#     with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
#         ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
#         with ui.row().classes('gap-4'):
#             ui.button('Home', on_click=lambda: ui.navigate.to('/')).classes('text-white hover:text-blue-300')
#             ui.button('Working Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('text-white hover:text-blue-300')
#             ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('text-white hover:text-blue-300')
#             ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('text-white hover:text-blue-300')
#             ui.button('Weekly Schedule', on_click=lambda: ui.navigate.to('/weekly-schedule')).classes('text-white hover:text-blue-300') # Added Weekly Schedule

#             # Conditional Training Preferences Link
#             if await is_preference_day():
#                  ui.button('Training Preferences', on_click=lambda: ui.navigate.to('/training-preferences')).classes('text-white hover:text-blue-300')

#             # Conditional Live Dashboard Link
#             if await user_has_active_session(user):
#                ui.button('Live Dashboard', on_click=lambda: ui.navigate.to('/live-dashboard')).classes('text-white hover:text-blue-300')

#             if user:
#                 with ui.column():
#                     user_button = ui.button(f'👤 {user.get("name", "Account")} ▾').classes('text-white')
#                     user_menu = ui.menu().props('auto-close').classes('bg-white text-black shadow-md rounded-md')

#                     with user_menu:
#                         ui.menu_item('My Profile', on_click=lambda: ui.navigate.to('/myprofile'))
#                         ui.menu_item('My Bookings', on_click=lambda: ui.navigate.to('/mybookings'))
#                         ui.menu_item('My Plans', on_click=lambda: ui.navigate.to('/mytrainingplans'))
#                         ui.menu_item('Logout', on_click=logout)
#                     user_button.on('click', user_menu.open)
#             else:
#                  ui.button('Login/Register', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('text-white hover:text-blue-300')
#     # --- End Copied Navbar ---

#     # Main content card
#     with ui.card().classes('w-full max-w-5xl p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-20'): # Added margin-top and max-width
#         ui.label('Weekly Training Schedule').classes('text-h4 text-center mb-4 text-blue-300')

#         # Container to hold schedule data
#         schedule_container = ui.column().classes('w-full')

#         # Get token from local storage
#         token_script = '''
#         const token = localStorage.getItem('token');
#         if (token) {
#             return token;
#         } else {
#             return null;
#         }
#         '''
        
#         @ui.refreshable
#         async def load_schedule():
#             # Get token
#             token = await ui.run_javascript(token_script)
#             if not token:
#                 ui.notify('Please log in to view the weekly schedule', color='negative')
#                 ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login') # Redirect to login
#                 return

#             # Get user info (already present)
#             user_info = await ui.run_javascript('''
#                 return JSON.parse(localStorage.getItem('user_info') || '{}');
#             ''')
#             user_type = user_info.get('user_type', '')
            
#             # Set up date selection
#             today = datetime.date.today()
#             # Find the most recent Sunday (start of week)
#             days_since_sunday = today.weekday() + 1  # +1 because Python's weekday() has Monday=0, Sunday=6
#             if days_since_sunday == 7:  # If today is Sunday
#                 days_since_sunday = 0
#             last_sunday = today - datetime.timedelta(days=days_since_sunday)
#             next_sunday = last_sunday + datetime.timedelta(days=7)
            
#             # Clear the container
#             with schedule_container:
#                 ui.spinner(size='lg').classes('self-center')
#                 ui.label('Loading schedule...').classes('self-center')
                
#             # Wait a bit to show the loading spinner
#             await asyncio.sleep(0.5)
#             schedule_container.clear()
            
#             with schedule_container:
#                 # Create date selection
#                 with ui.row().classes('w-full'):
#                     with ui.column().classes('w-1/2'):
#                         week_options = {
#                             "Current Week": last_sunday.strftime("%Y-%m-%d"),
#                             "Next Week": next_sunday.strftime("%Y-%m-%d")
#                         }
#                         selected_week_state = ui.state(list(week_options.values())[0])
                        
#                         dropdown = ui.select(
#                             options=list(week_options.keys()),
#                             value=list(week_options.keys())[0],
#                             label="Select Week"
#                         ).classes('w-full')
                        
#                         def on_week_change(e):
#                             selected_week_state.value = week_options[e.value]
#                             load_schedule_data(selected_week_state.value, user_type)
                        
#                         dropdown.on('update:model-value', on_week_change)
                    
#                     # For managers only - show Generate Schedule button
#                     if user_type == "manager":
#                         with ui.column().classes('w-1/2 items-end'):
#                             ui.button(
#                                 'Generate Schedule',
#                                 on_click=lambda: generate_schedule(selected_week_state.value)
#                             ).props('color=primary')
                
#                 # Display week dates
#                 week_start_date = datetime.datetime.strptime(selected_week_state.value, "%Y-%m-%d").date()
#                 week_end_date = week_start_date + datetime.timedelta(days=4)  # Sunday to Thursday
#                 ui.label(f"Week: {week_start_date.strftime('%d %b %Y')} to {week_end_date.strftime('%d %b %Y')}").classes('text-h6')
                
#                 # Container for the schedule tabs
#                 schedule_tabs_container = ui.element('div').classes('w-full')
                
#                 # Function to load schedule data
#                 async def load_schedule_data(selected_week, user_type):
#                     schedule_tabs_container.clear()
                    
#                     with schedule_tabs_container:
#                         ui.spinner(size='lg').classes('self-center')
#                         ui.label('Loading schedule data...').classes('self-center')
                    
#                     try:
#                         # Get schedule data based on user type
#                         if user_type == "member":
#                             response = await ui.run_javascript(f'''
#                                 async function getMemberSchedule() {{
#                                     const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/schedule/member/{{selected_week}}", {{
#                                         headers: {{
#                                             "Authorization": "Bearer " + localStorage.getItem('token')
#                                         }}
#                                     }});
#                                     return await response.json();
#                                 }}
#                                 return await getMemberSchedule();
#                             ''')
#                         else:
#                             response = await ui.run_javascript(f'''
#                                 async function getSchedule() {{
#                                     const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/schedule/{{selected_week}}", {{
#                                         headers: {{
#                                             "Authorization": "Bearer " + localStorage.getItem('token')
#                                         }}
#                                     }});
#                                     return await response.json();
#                                 }}
#                                 return await getSchedule();
#                             ''')
                        
#                         # Clear the container
#                         schedule_tabs_container.clear()
                        
#                         with schedule_tabs_container:
#                             if not response:
#                                 ui.label("No training sessions scheduled for this week.").classes('text-info')
#                             else:
#                                 # Create tabs for each day
#                                 days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
                                
#                                 with ui.tabs().classes('w-full') as tabs:
#                                     for day in days:
#                                         ui.tab(day).classes('text-lg')
                                
#                                 # Group schedule by day
#                                 schedule_by_day = {day: [] for day in days}
#                                 for session in response:
#                                     schedule_by_day[session["day_of_week"]].append(session)
                                
#                                 # Display schedule for each day
#                                 with ui.tab_panels(tabs, value=days[0]).classes('w-full'):
#                                     for day in days:
#                                         with ui.tab_panel(day):
#                                             day_schedule = schedule_by_day[day]
                                            
#                                             if not day_schedule:
#                                                 ui.label(f"No training sessions scheduled for {day}.").classes('text-info')
#                                             else:
#                                                 # Sort by start time
#                                                 day_schedule.sort(key=lambda x: x["start_time"])
                                                
#                                                 for session in day_schedule:
#                                                     with ui.card().classes('w-full q-my-sm'):
#                                                         with ui.expansion(
#                                                             f"{session['start_time']} - {session['end_time']} | {session['hall_name']} with {session['trainer_name']}"
#                                                         ).classes('w-full'):
#                                                             with ui.row().classes('w-full'):
#                                                                 with ui.column().classes('w-1/2'):
#                                                                     ui.label(f"📍 Hall: {session['hall_name']}").classes('text-bold')
#                                                                     ui.label(f"👨‍🏫 Trainer: {session['trainer_name']}")
#                                                                     ui.label(f"🕒 Time: {session['start_time']} - {session['end_time']}")
#                                                                     ui.label(f"📊 Status: {session['status']}").classes(
#                                                                         'text-positive' if session['status'] == 'Completed' else
#                                                                         'text-negative' if session['status'] == 'Cancelled' else
#                                                                         'text-primary' if session['status'] == 'In Progress' else
#                                                                         'text-secondary'
#                                                                     )
                                                                
#                                                                 with ui.column().classes('w-1/2'):
#                                                                     ui.label(f"👥 Capacity: {session['current_capacity']}/{session['max_capacity']}")
                                                                    
#                                                                     # Only show start session button for today's sessions that are scheduled
#                                                                     if (user_type == "trainer" or user_type == "manager"):
#                                                                         # Check if the session is today and scheduled
#                                                                         session_date = datetime.datetime.strptime(
#                                                                             f"{selected_week} {session['start_time']}", 
#                                                                             "%Y-%m-%d %H:%M:%S"
#                                                                         ).date()
                                                                        
#                                                                         if session["status"] == "Scheduled" and session_date == today:
#                                                                             ui.button(
#                                                                                 "Start Live Session",
#                                                                                 on_click=lambda s=session: start_live_session(s['schedule_id'])
#                                                                             ).props('color=positive')
                
#                     except Exception as e:
#                         schedule_tabs_container.clear()
#                         with schedule_tabs_container:
#                             ui.label(f"Failed to load schedule: {str(e)}").classes('text-negative')
                
#                 # Load initial schedule data
#                 await load_schedule_data(selected_week_state.value, user_type)
        
#         async def generate_schedule(week_start_date):
#             """Generate the weekly schedule for the selected week (manager only)"""
#             try:
#                 response = await ui.run_javascript(f'''
#                     async function generateSchedule() {{
#                         const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/schedule/generate/{week_start_date}", {{
#                             method: "POST",
#                             headers: {{
#                                 "Authorization": "Bearer " + localStorage.getItem('token')
#                             }}
#                         }});
#                         if (response.ok) {{
#                             return await response.json();
#                         }} else {{
#                             throw new Error("Failed to generate schedule");
#                         }}
#                     }}
#                     try {{
#                         return await generateSchedule();
#                     }} catch (e) {{
#                         return {{ error: e.toString() }};
#                     }}
#                 ''')
                
#                 if response and not response.get("error"):
#                     ui.notify("Weekly schedule generated successfully!", color="positive")
#                     load_schedule.refresh() # Use await if load_schedule becomes async
#                 else:
#                     ui.notify(f"Failed to generate schedule: {response.get('error', 'Unknown error')}", color="negative")

#             except Exception as e: # Added except block
#                 ui.notify(f"An error occurred during schedule generation: {str(e)}", color="negative")

#         async def start_live_session(schedule_id):
#             """Start a live training session for the selected schedule"""
#             try:
#                 # Create a new live session
#                 create_response = await ui.run_javascript(f'''
#                     async function createLiveSession() {{
#                         const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/live/sessions", {{
#                             method: "POST",
#                             headers: {{
#                                 "Authorization": "Bearer " + localStorage.getItem('token'),
#                                 "Content-Type": "application/json"
#                             }},
#                             body: JSON.stringify({{ "schedule_id": {schedule_id} }})
#                         }});
#                         if (response.ok) {{
#                             return await response.json();
#                         }} else {{
#                             throw new Error("Failed to create live session");
#                         }}
#                     }}
#                     try {{
#                         return await createLiveSession();
#                     }} catch (e) {{
#                         return {{ error: e.toString() }};
#                     }}
#                 ''')
                
#                 if create_response and not create_response.get("error"):
#                     live_session_id = create_response.get("live_session_id")
                    
#                     # Start the live session
#                     start_response = await ui.run_javascript(f'''
#                         async function startLiveSession() {{
#                             const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/live/sessions/{live_session_id}/start", {{
#                                 method: "POST",
#                                 headers: {{
#                                     "Authorization": "Bearer " + localStorage.getItem('token')
#                             }}
#                         }});
#                         if (response.ok) {{
#                             return await response.json();
#                         }} else {{
#                             throw new Error("Failed to start live session");
#                         }}
#                       }}
#                       try {{
#                           return await startLiveSession();
#                       }} catch (e) {{
#                           return {{ error: e.toString() }};
#                       }}
#                     ''')
                    
#                     if start_response and not start_response.get("error"):
#                         ui.notify("Live session started successfully!", color="positive")
#                         # Store active session in local storage
#                         await ui.run_javascript(f'''
#                             localStorage.setItem('active_live_session_id', '{live_session_id}');
#                         ''')
#                         # Redirect to live dashboard
#                         ui.navigate.to('/live-dashboard')
#                     else:
#                         ui.notify(f"Failed to start live session: {start_response.get('error', 'Unknown error')}", color="negative")
#                 else:
#                     ui.notify(f"Failed to create live session: {create_response.get('error', 'Unknown error')}", color="negative")

#             except Exception as e: # Added except block
#                 ui.notify(f"An error occurred starting the session: {str(e)}", color="negative")

#     # Add refresh button (Corrected Indentation)
#     with ui.row().classes('q-mt-md'):
#         ui.button('Refresh', on_click=load_schedule).props('color=primary')

#     # Initial load (Corrected Indentation)
#     await load_schedule()

# # Removed commented out timer and registration lines