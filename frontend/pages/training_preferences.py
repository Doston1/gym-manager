from nicegui import ui, app
import requests
import datetime
import json
import asyncio
import httpx
from ..config import API_HOST, API_PORT
from frontend.components.navbar import create_navbar_with_conditional_buttons, apply_page_style, get_current_user

async def is_preference_day():
    # Simple check for Thursday (weekday 3)
    return datetime.date.today().weekday() == 3

# Placeholder for checking active session - Requires Backend Implementation
async def user_has_active_session(user):
    if not user:
        return False
    try:
        token = await ui.run_javascript("localStorage.getItem('token')")
        if not token:
            return False
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            # This endpoint should check if the user (member/trainer) has a session NOW.
            response = await client.get(f"http://{API_HOST}:{API_PORT}/training/live/sessions/current", headers=headers)
            if response.status_code == 200 and response.json():
                return True
            return False
    except Exception as e:
        print(f"Error checking active session: {e}")
        return False


async def user_has_active_session_for_navbar():
    """Wrapper function for navbar condition checking"""
    try:
        user = await get_current_user()
        return await user_has_active_session(user)
    except Exception as e:
        print(f"Error checking active session: {e}")
        return False

async def display_training_preferences():
    # Apply consistent page styling
    apply_page_style()
    ui.query('.nicegui-content').classes('items-center')
    
    # Define conditional buttons
    conditional_buttons = [
        {
            'condition_func': is_preference_day,
            'label': 'Training Preferences',
            'on_click': lambda: ui.navigate.to('/training-preferences'),
            'classes': 'text-white hover:text-blue-300'
        },
        {
            'condition_func': user_has_active_session_for_navbar,
            'label': 'Live Dashboard',
            'on_click': lambda: ui.navigate.to('/live-dashboard'),
            'classes': 'text-white hover:text-blue-300'
        }
    ]

    # Additional standard buttons
    additional_buttons = [
        {
            'label': 'Weekly Schedule',
            'on_click': lambda: ui.navigate.to('/weekly-schedule'),
            'classes': 'text-white hover:text-blue-300'
        }
    ]

    # Create navbar with conditional buttons
    user = await create_navbar_with_conditional_buttons(check_functions=conditional_buttons)

    # Main content card
    with ui.card().classes('w-full max-w-4xl mx-auto p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-20'): # Added mx-auto for centering
        ui.label('Weekly Training Preferences').classes('text-h4 text-center mb-4 text-blue-300')

        # Container to hold preference form data
        preference_container = ui.column().classes('w-full')

        # Get token from local storage
        token_script = '''
        const token = localStorage.getItem('token');
        if (token) {
            return token;
        } else {
            return null;
        }
        '''
        
        @ui.refreshable
        async def load_preferences():
            # Get token
            token = await ui.run_javascript(token_script)
            if not token:
                ui.notify('Please log in to view training preferences', color='negative')
                ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login') # Redirect to login
                return
                
            # Check if we can set preferences today
            with preference_container:
                ui.spinner(size='lg').classes('self-center')
                ui.label('Loading preferences...').classes('self-center text-white')
                
            headers = {"Authorization": f"Bearer {token}"}
            
            try:
                # Check if we can set preferences today
                response = await ui.run_javascript(f'''
                    async function checkPreferences() {{
                        const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/preferences/check", {{
                            headers: {{
                                "Authorization": "Bearer " + localStorage.getItem('token')
                            }}
                        }});
                        return await response.json();
                    }}
                    return await checkPreferences();
                ''')
                
                # Debug: Print the response
                print(f"API Response: {response}")
                
                # Clear the container
                preference_container.clear()
                
                # Parse the response
                if response and not response.get("detail"):  # Check for API error details
                    can_set_preferences = response.get("can_set_preferences", False)
                    week_start_date = response.get("week_start_date", "")
                    existing_preferences = response.get("preferences", [])
                    
                    # Display week dates
                    week_end_date_obj = datetime.datetime.strptime(week_start_date, "%Y-%m-%d").date() + datetime.timedelta(days=4)
                    week_end_date = week_end_date_obj.strftime("%Y-%m-%d")
                    
                    with preference_container:
                        ui.label(f"Training Week: {week_start_date} to {week_end_date}").classes('text-h5 text-white')
                        
                        if can_set_preferences:
                            ui.label('Today you can set your training preferences for next week!').classes('text-positive')
                        else:
                            ui.label('You can only set preferences on Thursdays. Today you can only view your existing preferences.').classes('text-warning')
                        
                        # Get trainers for selection
                        trainers_response = await ui.run_javascript(f'''
                            async function getTrainers() {{
                                const response = await fetch("http://{API_HOST}:{API_PORT}/users/trainers", {{
                                    headers: {{
                                        "Authorization": "Bearer " + localStorage.getItem('token')
                                    }}
                                }});
                                return await response.json();
                            }}
                            return await getTrainers();
                        ''')
                        
                        trainers = trainers_response or []
                        
                        # Create a trainer selection box
                        trainer_options = [{"label": "No Preference", "value": None}]
                        trainer_options.extend([{"label": f"{t['first_name']} {t['last_name']}", "value": t['trainer_id']} for t in trainers])
                        
                        # Create a time slots grid for each day
                        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
                        
                        # Define time slots (1.5-hour blocks)
                        start_hour = 8  # 8 AM
                        end_hour = 21   # 9 PM
                        time_slots = []
                        
                        for hour in range(start_hour, end_hour):
                            time_slots.append(f"{hour:02d}:00-{hour+1:02d}:30")
                        
                        # Convert existing preferences to a more usable format
                        existing_prefs = {}
                        for pref in existing_preferences:
                            day = pref["day_of_week"]
                            time_key = f"{pref['start_time']}-{pref['end_time']}"
                            existing_prefs[(day, time_key)] = {
                                "preference_id": pref["preference_id"],
                                "preference_type": pref["preference_type"],
                                "trainer_id": pref["trainer_id"]
                            }
                        
                        # Create tabs for each day
                        with ui.tabs().classes('w-full') as tabs:
                            for day in days:
                                ui.tab(day).classes('text-lg')
                        
                        with ui.tab_panels(tabs, value=days[0]).classes('w-full'):
                            for day in days:
                                with ui.tab_panel(day):
                                    ui.label(f"{day} Preferences").classes('text-h6 text-black')
                                    
                                    for time_slot in time_slots:
                                        start_time, end_time = time_slot.split('-')
                                        
                                        # Check if there's an existing preference
                                        existing = existing_prefs.get((day, f"{start_time}:00-{end_time}:00"), None)
                                        
                                        with ui.card().classes('w-full q-my-sm'):
                                            with ui.row().classes('w-full items-center'):
                                                ui.label(time_slot).classes('text-bold text-lg text-black')
                                                
                                                with ui.column().classes('w-2/3'):
                                                    # Default values based on existing preferences
                                                    default_pref = "Not Selected"
                                                    default_trainer_id = None
                                                    
                                                    if existing:
                                                        if existing["preference_type"] == "Preferred":
                                                            default_pref = "Preferred"
                                                        elif existing["preference_type"] == "Available":
                                                            default_pref = "Available"
                                                        
                                                        default_trainer_id = existing["trainer_id"]
                                                    
                                                    # Create a unique key for each preference selector
                                                    pref_key = f"pref_{day}_{time_slot}"
                                                    trainer_key = f"trainer_{day}_{time_slot}"
                                                    
                                                    # Create preference select
                                                    pref_options = ["Not Selected", "Preferred", "Available"]
                                                    pref_select = ui.select(
                                                        pref_options, 
                                                        label="Preference:",
                                                        value=default_pref
                                                    ).props('outlined').classes('w-full')
                                                    if not can_set_preferences:
                                                        pref_select.disable()
                                                    
                                                    # For storing trainer ID
                                                    trainer_id_state = {'value': default_trainer_id}
                                                    
                                                    # Only show trainer selection if preference is set
                                                    trainer_select_container = ui.element('div').classes('w-full')
                                                    
                                                    with trainer_select_container:
                                                        if default_pref != "Not Selected":
                                                            # Find default trainer index
                                                            default_trainer_option = next(
                                                                (t for t in trainer_options if t["value"] == default_trainer_id), 
                                                                trainer_options[0]
                                                            )
                                                            
                                                            trainer_select = ui.select(
                                                                [t["label"] for t in trainer_options],
                                                                label="Preferred Trainer:",
                                                                value=default_trainer_option["label"]
                                                            ).props('outlined').classes('w-full')
                                                            if not can_set_preferences:
                                                                trainer_select.disable()
                                                            
                                                            # Handle trainer selection change
                                                            def on_trainer_change(e):
                                                                selected_label = e.value
                                                                selected_trainer = next(
                                                                    (t for t in trainer_options if t["label"] == selected_label),
                                                                    trainer_options[0]
                                                                )
                                                                trainer_id_state['value'] = selected_trainer["value"]
                                                                update_preference(day, start_time, end_time, pref_select.value, trainer_id_state['value'], existing)
                                                            
                                                            trainer_select.on('update:model-value', on_trainer_change)
                                                    
                                                # Handle preference change
                                                def on_pref_change(e):
                                                    preference = e.value
                                                    
                                                    # Clear and update trainer selection when preference changes
                                                    trainer_select_container.clear()
                                                    
                                                    with trainer_select_container:
                                                        if preference != "Not Selected":
                                                            trainer_select = ui.select(
                                                                [t["label"] for t in trainer_options],
                                                                label="Preferred Trainer:",
                                                                value=trainer_options[0]["label"]
                                                            ).props('outlined').classes('w-full')
                                                            if not can_set_preferences:
                                                                trainer_select.disable()
                                                            
                                                            # Handle trainer selection change
                                                            def on_new_trainer_change(e):
                                                                selected_label = e.value
                                                                selected_trainer = next(
                                                                    (t for t in trainer_options if t["label"] == selected_label),
                                                                    trainer_options[0]
                                                                )
                                                                trainer_id_state['value'] = selected_trainer["value"]
                                                                update_preference(day, start_time, end_time, preference, trainer_id_state['value'], existing)
                                                            
                                                            trainer_select.on('update:model-value', on_new_trainer_change)
                                                    
                                                    update_preference(day, start_time, end_time, preference, trainer_id_state['value'], existing)
                                                
                                                pref_select.on('update:model-value', on_pref_change)
                else:
                    # API call failed or returned an error
                    with preference_container:
                        if response and response.get("detail"):
                            ui.label(f"API Error: {response.get('detail')}").classes('text-negative')
                        else:
                            ui.label("Failed to load preferences from server.").classes('text-negative')
                        
                        # Show basic information even when API fails
                        today = datetime.date.today()
                        is_thursday = today.weekday() == 3
                        
                        # Calculate next week's start date (Sunday)
                        days_until_sunday = (6 - today.weekday()) % 7
                        if days_until_sunday == 0:  # If today is Sunday
                            days_until_sunday = 7  # Get next Sunday
                        next_week_start = today + datetime.timedelta(days=days_until_sunday)
                        week_end_date = next_week_start + datetime.timedelta(days=4)
                        
                        ui.label(f"Training Week: {next_week_start.strftime('%Y-%m-%d')} to {week_end_date.strftime('%Y-%m-%d')}").classes('text-h5 text-white')
                        
                        if is_thursday:
                            ui.label('Today you can set your training preferences for next week!').classes('text-positive')
                        else:
                            ui.label('You can only set preferences on Thursdays. Today you can only view your existing preferences.').classes('text-warning')
                        
                        ui.label("Please check your login status and try refreshing the page.").classes('text-info')
            
            except Exception as e:
                with preference_container:
                    ui.label(f"An error occurred: {str(e)}").classes('text-negative')
        
        async def update_preference(day, start_time, end_time, preference, trainer_id, existing):
            """Update preference via API call"""
            if not await ui.run_javascript(token_script):
                ui.notify('Please log in to update preferences', color='negative')
                return
                
            try:
                # If changing from Not Selected to a preference
                if preference != "Not Selected" and (not existing or existing["preference_type"] == "Not Selected"):
                    # Create new preference
                    new_pref = {
                        "member_id": await get_member_id(),
                        "day_of_week": day,
                        "start_time": f"{start_time}:00",
                        "end_time": f"{end_time}:00",
                        "preference_type": preference,
                        "trainer_id": trainer_id,
                        "week_start_date": await get_next_week_start_date()
                    }
                    
                    response = await ui.run_javascript(f'''
                        async function createPreference() {{
                            const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/preferences", {{
                                method: "POST",
                                headers: {{
                                    "Authorization": "Bearer " + localStorage.getItem('token'),
                                    "Content-Type": "application/json"
                            }},
                            body: JSON.stringify({json.dumps(new_pref)})
                        }});
                        if (response.ok) {{
                            return await response.json();
                        }} else {{
                            throw new Error("Failed to create preference");
                        }}
                    }}
                    try {{
                        return await createPreference();
                    }} catch (e) {{
                        return {{ error: e.toString() }};
                    }}
                    ''')
                    
                    if response and not response.get("error"):
                        ui.notify(f"Preference for {day} {start_time}-{end_time} created", color='positive')
                    else:
                        ui.notify(f"Failed to create preference: {response.get('error', 'Unknown error')}", color='negative')
                
                # If changing from a preference to Not Selected
                elif preference == "Not Selected" and existing and existing["preference_type"] != "Not Selected":
                    preference_id = existing["preference_id"]
                    
                    response = await ui.run_javascript(f'''
                        async function deletePreference() {{
                            const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/preferences/{preference_id}", {{
                                method: "DELETE",
                                headers: {{
                                    "Authorization": "Bearer " + localStorage.getItem('token')
                            }}
                        }});
                        if (response.ok) {{
                            return await response.json();
                        }} else {{
                            throw new Error("Failed to delete preference");
                        }}
                    }}
                    try {{
                        return await deletePreference();
                    }} catch (e) {{
                        return {{ error: e.toString() }};
                    }}
                    ''')
                    
                    if response and not response.get("error"):
                        ui.notify(f"Preference for {day} {start_time}-{end_time} deleted", color='positive')
                    else:
                        ui.notify(f"Failed to delete preference: {response.get('error', 'Unknown error')}", color='negative')
                
                # If updating an existing preference
                elif existing and (existing["preference_type"] != preference or existing["trainer_id"] != trainer_id):
                    preference_id = existing["preference_id"]
                    update_data = {
                        "preference_type": preference,
                        "trainer_id": trainer_id
                    }
                    
                    response = await ui.run_javascript(f'''
                        async function updatePreference() {{
                            const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/preferences/{preference_id}", {{
                                method: "PUT",
                                headers: {{
                                    "Authorization": "Bearer " + localStorage.getItem('token'),
                                    "Content-Type": "application/json"
                            }},
                            body: JSON.stringify({json.dumps(update_data)})
                        }});
                        if (response.ok) {{
                            return await response.json();
                        }} else {{
                            throw new Error("Failed to update preference");
                        }}
                    }}
                    try {{
                        return await updatePreference();
                    }} catch (e) {{
                        return {{ error: e.toString() }};
                    }}
                    ''')
                    
                    if response and not response.get("error"):
                        ui.notify(f"Preference for {day} {start_time}-{end_time} updated", color='positive')
                    else:
                        ui.notify(f"Failed to update preference: {response.get('error', 'Unknown error')}", color='negative')
            
            except Exception as e:
                ui.notify(f"An error occurred: {str(e)}", color='negative')
        
        async def get_member_id():
            """Get the current member ID"""
            user_info = await ui.run_javascript('''
                return JSON.parse(localStorage.getItem('user_info') || '{}');
            ''')
            return user_info.get("member_id")
        
        async def get_next_week_start_date():
            """Get the start date of the next week"""
            response = await ui.run_javascript(f'''
                async function getNextWeekDate() {{
                    const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/preferences/check", {{
                        headers: {{
                            "Authorization": "Bearer " + localStorage.getItem('token')
                        }}
                    }});
                    const data = await response.json();
                    return data.week_start_date;
                }}
                return await getNextWeekDate();
            ''')
            return response
        
        # Add refresh button
        with ui.row().classes('q-mt-md'):
            ui.button('Refresh', on_click=lambda: load_preferences.refresh()).props('color=primary')
        
        # Initial load
        await load_preferences()

        # Remove the timer-based auto-refresh if not desired, or keep it
        # async def auto_refresh():
        #     while True:
        #         await asyncio.sleep(300)  # 5 minutes
        #         await load_preferences.refresh() # Use await

        # ui.timer(0.1, lambda: asyncio.create_task(auto_refresh()))

# Make sure the page registration uses the async function
# This should be done in ui.py:
# ui.page('/training-preferences')(display_training_preferences)