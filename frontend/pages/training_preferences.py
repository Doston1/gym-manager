from nicegui import ui
import datetime
from frontend.config import API_HOST, API_PORT
from frontend.utils import api_call, get_current_user_details
import asyncio

async def display_training_preferences():
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    ui.query('.nicegui-content').classes('items-center')

    user = await get_current_user_details()
    if not user or user.get("user_type") != "member":
        ui.label("You must be a logged-in member to set preferences.").classes('text-xl m-auto')
        if not user: ui.button("Login", on_click=lambda: ui.navigate.to(f"http://{API_HOST}:{API_PORT}/login"))
        return

    # --- Navbar (simplified for brevity, reuse from home_page.py logic) ---
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold').on('click', lambda: ui.navigate.to('/'))
        # ... (add other nav buttons) ...

    # --- Main Content ---
    with ui.card().classes('w-full max-w-4xl p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-4'):
        ui.label('Weekly Training Preferences').classes('text-3xl font-bold text-center mb-6 text-blue-300')

        preferences_container = ui.column().classes('w-full gap-4')
        
        # State for selected week start date
        # Calculate next week's Sunday
        today = datetime.date.today()
        days_until_next_sunday = (6 - today.weekday() + 7) % 7
        if days_until_next_sunday == 0 and today.weekday() != 6: # if today is not sunday but calculation is 0, means next sunday
            days_until_next_sunday = 7
        elif today.weekday() == 6: # if today is sunday, schedule for next sunday
             days_until_next_sunday = 7
        next_week_start_date_obj = today + datetime.timedelta(days=days_until_next_sunday)
        next_week_start_date_iso = next_week_start_date_obj.isoformat()

        async def load_and_display_preferences():
            preferences_container.clear()
            with preferences_container:
                if datetime.date.today().weekday() != 3: # Thursday
                    ui.label("Preferences can only be set/modified on Thursdays.").classes("text-warning text-lg text-center")
                
                ui.label(f"Setting preferences for week starting: {next_week_start_date_iso} (Sunday)").classes("text-xl mb-4 text-center")

                # Fetch existing preferences for this week
                existing_prefs_data = await api_call("GET", f"/training-preferences/member/week/{next_week_start_date_iso}")
                existing_preferences = {}
                if existing_prefs_data:
                    for p in existing_prefs_data:
                        key = (p['day_of_week'], p['start_time'])
                        existing_preferences[key] = p

                # Fetch trainers for preferred trainer dropdown
                trainers_data = await api_call("GET", "/users/trainers") # Assuming an endpoint like this exists
                trainer_options = {None: "No Preference"}
                if trainers_data:
                    for t in trainers_data: # trainers_data should be list of UserResponse with trainer_id
                        if t.get('trainer_id'): # Ensure trainer_id is present
                             trainer_options[t['trainer_id']] = f"{t['first_name']} {t['last_name']}"


                days_of_week_for_pref = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"] # Member sets for Sun-Thu
                time_slots = [f"{h:02d}:00" for h in range(8, 22)] # Example: 8 AM to 9 PM, 1-hour slots for simplicity

                with ui.tabs().classes('w-full') as tabs:
                    for day_name in days_of_week_for_pref:
                        ui.tab(day_name)
                
                with ui.tab_panels(tabs, value=days_of_week_for_pref[0]).classes('w-full'):
                    for day_name in days_of_week_for_pref:
                        with ui.tab_panel(day_name):
                            ui.label(day_name).classes("text-2xl font-semibold mb-2")
                            for start_hour_str in time_slots:
                                start_time_obj = datetime.datetime.strptime(start_hour_str, "%H:%M").time()
                                # Assuming 1.5 hour slots for now as in your example
                                end_time_obj = (datetime.datetime.combine(datetime.date.min, start_time_obj) + datetime.timedelta(hours=1, minutes=30)).time()
                                
                                time_display = f"{start_time_obj.strftime('%H:%M')} - {end_time_obj.strftime('%H:%M')}"
                                current_pref_key = (day_name, start_time_obj.isoformat(timespec='seconds'))
                                current_pref_details = existing_preferences.get(current_pref_key)

                                with ui.card().classes("w-full p-3 my-1 bg-gray-800"):
                                    with ui.row().classes("w-full items-center justify-between"):
                                        ui.label(time_display).classes("text-lg")
                                        
                                        pref_type_val = current_pref_details['preference_type'] if current_pref_details else "Not Available"
                                        trainer_id_val = current_pref_details['trainer_id'] if current_pref_details else None

                                        select_pref_type = ui.select(
                                            options=["Preferred", "Available", "Not Available"],
                                            value=pref_type_val,
                                            label="Your Preference"
                                        ).props("dense outlined bg-color=white text-black").classes("w-48")
                                        
                                        select_trainer = ui.select(
                                            options=trainer_options,
                                            value=trainer_id_val,
                                            label="Preferred Trainer"
                                        ).props("dense outlined bg-color=white text-black").classes("w-48")

                                        async def handle_save_preference(day, start_t, end_t, pref_select, train_select):
                                            if datetime.date.today().weekday() != 3:
                                                ui.notify("Preferences can only be set/modified on Thursdays.", color='warning')
                                                return

                                            payload = {
                                                "member_id": user['member_id'],
                                                "week_start_date": next_week_start_date_iso,
                                                "day_of_week": day,
                                                "start_time": start_t.isoformat(timespec='seconds'),
                                                "end_time": end_t.isoformat(timespec='seconds'),
                                                "preference_type": pref_select.value,
                                                "trainer_id": train_select.value if train_select.value != "No Preference" else None
                                            }
                                            
                                            # If "Not Available" and preference exists, consider it a delete or update to Not Available
                                            # The backend POST /training-preferences handles create/update based on unique key
                                            result = await api_call("POST", "/training-preferences", payload=payload)
                                            if result:
                                                ui.notify(f"Preference for {day} {time_display} saved!", color='positive')
                                                await load_and_display_preferences() # Refresh to show updated state
                                            else:
                                                ui.notify(f"Failed to save preference.", color='negative')

                                        ui.button("Save", on_click=lambda day=day_name, st=start_time_obj, et=end_time_obj, ps=select_pref_type, ts=select_trainer: handle_save_preference(day, st, et, ps, ts)).props("color=primary")
        
        await load_and_display_preferences()

# ====== OLD VERSION ======

# from nicegui import ui, app # Added app import
# import requests
# import datetime
# from ..config import API_HOST, API_PORT # Added API_HOST, API_PORT
# import json
# import asyncio
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
#                 # Store user info including type and ID if available
#                 user_data = response.json()
#                 await ui.run_javascript(f"localStorage.setItem('user_info', '{json.dumps(user_data)}');")
#                 return user_data
#     except Exception as e:
#         print(f"Error getting current user: {e}")
#     return None

# def logout():
#     ui.run_javascript("localStorage.removeItem('token'); localStorage.removeItem('user_info'); location.reload();")
#     # Redirect to backend logout which handles Auth0 logout
#     ui.navigate.to(f"http://{API_HOST}:{API_PORT}/logout")

# async def is_preference_day():
#     # Simple check for Thursday (weekday 3)
#     return datetime.date.today().weekday() == 3

# # --- End Copied Helper Functions ---


# async def display_training_preferences(): # Made async
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

#             # Conditional Live Dashboard Link (Needs backend check)
#             # Placeholder: Add logic here later if needed, requires async check
#             # if await user_has_active_session(user): # Example function
#             #    ui.button('Live Dashboard', on_click=lambda: ui.navigate.to('/live-dashboard')).classes('text-white hover:text-blue-300')


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
#                  # Optionally show login button if no user
#                  ui.button('Login/Register', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('text-white hover:text-blue-300')
#     # --- End Copied Navbar ---

#     # Main content card
#     with ui.card().classes('w-full max-w-4xl p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-20'): # Added margin-top
#         ui.label('Weekly Training Preferences').classes('text-h4 text-center mb-4 text-blue-300')

#         # Container to hold preference form data
#         preference_container = ui.column().classes('w-full')

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
#         async def load_preferences():
#             # Get token
#             token = await ui.run_javascript(token_script)
#             if not token:
#                 ui.notify('Please log in to view training preferences', color='negative')
#                 ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login') # Redirect to login
#                 return
                
#             # Check if we can set preferences today
#             with preference_container:
#                 ui.spinner(size='lg').classes('self-center')
#                 ui.label('Loading preferences...').classes('self-center')
                
#             headers = {"Authorization": f"Bearer {token}"}
            
#             try:
#                 # Check if we can set preferences today
#                 response = await ui.run_javascript(f'''
#                     async function checkPreferences() {{
#                         const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/preferences/check", {{
#                             headers: {{
#                                 "Authorization": "Bearer " + localStorage.getItem('token')
#                             }}
#                         }});
#                         return await response.json();
#                     }}
#                     return await checkPreferences();
#                 ''')
                
#                 # Clear the container
#                 preference_container.clear()
                
#                 # Parse the response
#                 if response:
#                     can_set_preferences = response.get("can_set_preferences", False)
#                     week_start_date = response.get("week_start_date", "")
#                     existing_preferences = response.get("preferences", [])
                    
#                     # Display week dates
#                     week_end_date_obj = datetime.datetime.strptime(week_start_date, "%Y-%m-%d").date() + datetime.timedelta(days=4)
#                     week_end_date = week_end_date_obj.strftime("%Y-%m-%d")
                    
#                     with preference_container:
#                         ui.label(f"Training Week: {week_start_date} to {week_end_date}").classes('text-h5')
                        
#                         if can_set_preferences:
#                             ui.label('Today you can set your training preferences for next week!').classes('text-positive')
#                         else:
#                             ui.label('You can only set preferences on Thursdays. Today you can only view your existing preferences.').classes('text-warning')
                        
#                         # Get trainers for selection
#                         trainers_response = await ui.run_javascript(f'''
#                             async function getTrainers() {{
#                                 const response = await fetch("http://{API_HOST}:{API_PORT}/users/trainers", {{
#                                     headers: {{
#                                         "Authorization": "Bearer " + localStorage.getItem('token')
#                                     }}
#                                 }});
#                                 return await response.json();
#                             }}
#                             return await getTrainers();
#                         ''')
                        
#                         trainers = trainers_response or []
                        
#                         # Create a trainer selection box
#                         trainer_options = [{"label": "No Preference", "value": None}]
#                         trainer_options.extend([{"label": f"{t['first_name']} {t['last_name']}", "value": t['trainer_id']} for t in trainers])
                        
#                         # Create a time slots grid for each day
#                         days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
                        
#                         # Define time slots (1.5-hour blocks)
#                         start_hour = 8  # 8 AM
#                         end_hour = 21   # 9 PM
#                         time_slots = []
                        
#                         for hour in range(start_hour, end_hour):
#                             time_slots.append(f"{hour:02d}:00-{hour+1:02d}:30")
                        
#                         # Convert existing preferences to a more usable format
#                         existing_prefs = {}
#                         for pref in existing_preferences:
#                             day = pref["day_of_week"]
#                             time_key = f"{pref['start_time']}-{pref['end_time']}"
#                             existing_prefs[(day, time_key)] = {
#                                 "preference_id": pref["preference_id"],
#                                 "preference_type": pref["preference_type"],
#                                 "trainer_id": pref["trainer_id"]
#                             }
                        
#                         # Create tabs for each day
#                         with ui.tabs().classes('w-full') as tabs:
#                             for day in days:
#                                 ui.tab(day).classes('text-lg')
                        
#                         with ui.tab_panels(tabs, value=days[0]).classes('w-full'):
#                             for day in days:
#                                 with ui.tab_panel(day):
#                                     ui.label(f"{day} Preferences").classes('text-h6')
                                    
#                                     for time_slot in time_slots:
#                                         start_time, end_time = time_slot.split('-')
                                        
#                                         # Check if there's an existing preference
#                                         existing = existing_prefs.get((day, f"{start_time}:00-{end_time}:00"), None)
                                        
#                                         with ui.card().classes('w-full q-my-sm'):
#                                             with ui.row().classes('w-full items-center'):
#                                                 ui.label(time_slot).classes('text-bold text-lg')
                                                
#                                                 with ui.column().classes('w-2/3'):
#                                                     # Default values based on existing preferences
#                                                     default_pref = "Not Selected"
#                                                     default_trainer_id = None
                                                    
#                                                     if existing:
#                                                         if existing["preference_type"] == "Preferred":
#                                                             default_pref = "Preferred"
#                                                         elif existing["preference_type"] == "Available":
#                                                             default_pref = "Available"
                                                        
#                                                         default_trainer_id = existing["trainer_id"]
                                                    
#                                                     # Create a unique key for each preference selector
#                                                     pref_key = f"pref_{day}_{time_slot}"
#                                                     trainer_key = f"trainer_{day}_{time_slot}"
                                                    
#                                                     # Create preference select
#                                                     pref_options = ["Not Selected", "Preferred", "Available"]
#                                                     pref_select = ui.select(
#                                                         pref_options, 
#                                                         label="Preference:",
#                                                         value=default_pref
#                                                     ).props('outlined').classes('w-full')
#                                                     pref_select.disable(not can_set_preferences)
                                                    
#                                                     # For storing trainer ID
#                                                     trainer_id_state = ui.state(default_trainer_id)
                                                    
#                                                     # Only show trainer selection if preference is set
#                                                     trainer_select_container = ui.element('div').classes('w-full')
                                                    
#                                                     with trainer_select_container:
#                                                         if default_pref != "Not Selected":
#                                                             # Find default trainer index
#                                                             default_trainer_option = next(
#                                                                 (t for t in trainer_options if t["value"] == default_trainer_id), 
#                                                                 trainer_options[0]
#                                                             )
                                                            
#                                                             trainer_select = ui.select(
#                                                                 [t["label"] for t in trainer_options],
#                                                                 label="Preferred Trainer:",
#                                                                 value=default_trainer_option["label"]
#                                                             ).props('outlined').classes('w-full')
#                                                             trainer_select.disable(not can_set_preferences)
                                                            
#                                                             # Handle trainer selection change
#                                                             def on_trainer_change(e):
#                                                                 selected_label = e.value
#                                                                 selected_trainer = next(
#                                                                     (t for t in trainer_options if t["label"] == selected_label),
#                                                                     trainer_options[0]
#                                                                 )
#                                                                 trainer_id_state.value = selected_trainer["value"]
#                                                                 update_preference(day, start_time, end_time, pref_select.value, trainer_id_state.value, existing)
                                                            
#                                                             trainer_select.on('update:model-value', on_trainer_change)
                                                    
#                                                 # Handle preference change
#                                                 def on_pref_change(e):
#                                                     preference = e.value
                                                    
#                                                     # Clear and update trainer selection when preference changes
#                                                     trainer_select_container.clear()
                                                    
#                                                     with trainer_select_container:
#                                                         if preference != "Not Selected":
#                                                             trainer_select = ui.select(
#                                                                 [t["label"] for t in trainer_options],
#                                                                 label="Preferred Trainer:",
#                                                                 value=trainer_options[0]["label"]
#                                                             ).props('outlined').classes('w-full')
#                                                             trainer_select.disable(not can_set_preferences)
                                                            
#                                                             # Handle trainer selection change
#                                                             def on_new_trainer_change(e):
#                                                                 selected_label = e.value
#                                                                 selected_trainer = next(
#                                                                     (t for t in trainer_options if t["label"] == selected_label),
#                                                                     trainer_options[0]
#                                                                 )
#                                                                 trainer_id_state.value = selected_trainer["value"]
#                                                                 update_preference(day, start_time, end_time, preference, trainer_id_state.value, existing)
                                                            
#                                                             trainer_select.on('update:model-value', on_new_trainer_change)
                                                    
#                                                     update_preference(day, start_time, end_time, preference, trainer_id_state.value, existing)
                                                
#                                                 pref_select.on('update:model-value', on_pref_change)
#                 else:
#                     with preference_container:
#                         ui.label("Failed to load preferences. Please try again.").classes('text-negative')
            
#             except Exception as e:
#                 with preference_container:
#                     ui.label(f"An error occurred: {str(e)}").classes('text-negative')
        
#         async def update_preference(day, start_time, end_time, preference, trainer_id, existing):
#             """Update preference via API call"""
#             if not await ui.run_javascript(token_script):
#                 ui.notify('Please log in to update preferences', color='negative')
#                 return
                
#             try:
#                 # If changing from Not Selected to a preference
#                 if preference != "Not Selected" and (not existing or existing["preference_type"] == "Not Selected"):
#                     # Create new preference
#                     new_pref = {
#                         "member_id": await get_member_id(),
#                         "day_of_week": day,
#                         "start_time": f"{start_time}:00",
#                         "end_time": f"{end_time}:00",
#                         "preference_type": preference,
#                         "trainer_id": trainer_id,
#                         "week_start_date": await get_next_week_start_date()
#                     }
                    
#                     response = await ui.run_javascript(f'''
#                         async function createPreference() {{
#                             const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/preferences", {{
#                                 method: "POST",
#                                 headers: {{
#                                     "Authorization": "Bearer " + localStorage.getItem('token'),
#                                     "Content-Type": "application/json"
#                             }},
#                             body: JSON.stringify({json.dumps(new_pref)})
#                         }});
#                         if (response.ok) {{
#                             return await response.json();
#                         }} else {{
#                             throw new Error("Failed to create preference");
#                         }}
#                     }}
#                     try {{
#                         return await createPreference();
#                     }} catch (e) {{
#                         return {{ error: e.toString() }};
#                     }}
#                     ''')
                    
#                     if response and not response.get("error"):
#                         ui.notify(f"Preference for {day} {start_time}-{end_time} created", color='positive')
#                     else:
#                         ui.notify(f"Failed to create preference: {response.get('error', 'Unknown error')}", color='negative')
                
#                 # If changing from a preference to Not Selected
#                 elif preference == "Not Selected" and existing and existing["preference_type"] != "Not Selected":
#                     preference_id = existing["preference_id"]
                    
#                     response = await ui.run_javascript(f'''
#                         async function deletePreference() {{
#                             const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/preferences/{preference_id}", {{
#                                 method: "DELETE",
#                                 headers: {{
#                                     "Authorization": "Bearer " + localStorage.getItem('token')
#                             }}
#                         }});
#                         if (response.ok) {{
#                             return await response.json();
#                         }} else {{
#                             throw new Error("Failed to delete preference");
#                         }}
#                     }}
#                     try {{
#                         return await deletePreference();
#                     }} catch (e) {{
#                         return {{ error: e.toString() }};
#                     }}
#                     ''')
                    
#                     if response and not response.get("error"):
#                         ui.notify(f"Preference for {day} {start_time}-{end_time} deleted", color='positive')
#                     else:
#                         ui.notify(f"Failed to delete preference: {response.get('error', 'Unknown error')}", color='negative')
                
#                 # If updating an existing preference
#                 elif existing and (existing["preference_type"] != preference or existing["trainer_id"] != trainer_id):
#                     preference_id = existing["preference_id"]
#                     update_data = {
#                         "preference_type": preference,
#                         "trainer_id": trainer_id
#                     }
                    
#                     response = await ui.run_javascript(f'''
#                         async function updatePreference() {{
#                             const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/preferences/{preference_id}", {{
#                                 method: "PUT",
#                                 headers: {{
#                                     "Authorization": "Bearer " + localStorage.getItem('token'),
#                                     "Content-Type": "application/json"
#                             }},
#                             body: JSON.stringify({json.dumps(update_data)})
#                         }});
#                         if (response.ok) {{
#                             return await response.json();
#                         }} else {{
#                             throw new Error("Failed to update preference");
#                         }}
#                     }}
#                     try {{
#                         return await updatePreference();
#                     }} catch (e) {{
#                         return {{ error: e.toString() }};
#                     }}
#                     ''')
                    
#                     if response and not response.get("error"):
#                         ui.notify(f"Preference for {day} {start_time}-{end_time} updated", color='positive')
#                     else:
#                         ui.notify(f"Failed to update preference: {response.get('error', 'Unknown error')}", color='negative')
            
#             except Exception as e:
#                 ui.notify(f"An error occurred: {str(e)}", color='negative')
        
#         async def get_member_id():
#             """Get the current member ID"""
#             user_info = await ui.run_javascript('''
#                 return JSON.parse(localStorage.getItem('user_info') || '{}');
#             ''')
#             return user_info.get("member_id")
        
#         async def get_next_week_start_date():
#             """Get the start date of the next week"""
#             response = await ui.run_javascript(f'''
#                 async function getNextWeekDate() {{
#                     const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/preferences/check", {{
#                         headers: {{
#                             "Authorization": "Bearer " + localStorage.getItem('token')
#                         }}
#                     }});
#                     const data = await response.json();
#                     return data.week_start_date;
#                 }}
#                 return await getNextWeekDate();
#             ''')
#             return response
        
#         # Add refresh button
#         with ui.row().classes('q-mt-md'):
#             ui.button('Refresh', on_click=load_preferences).props('color=primary')
        
#         # Initial load
#         await load_preferences()

#         # Remove the timer-based auto-refresh if not desired, or keep it
#         # async def auto_refresh():
#         #     while True:
#         #         await asyncio.sleep(300)  # 5 minutes
#         #         await load_preferences.refresh() # Use await

#         # ui.timer(0.1, lambda: asyncio.create_task(auto_refresh()))

# # Make sure the page registration uses the async function
# # This should be done in ui.py:
# # ui.page('/training-preferences')(display_training_preferences)