from nicegui import ui, app # Added app import
import requests
import datetime
import json
import asyncio
from ..config import API_HOST, API_PORT 
import httpx # Added httpx import

# --- Copied Helper Functions ---
async def get_current_user():
    try:
        token = await ui.run_javascript(
            "localStorage.getItem('token')",
            timeout=5.0
        )
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://{API_HOST}:{API_PORT}/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                await ui.run_javascript(f"localStorage.setItem('user_info', '{json.dumps(user_data)}');")
                return user_data
    except Exception as e:
        print(f"Error getting current user: {e}")
    return None

def logout():
    ui.run_javascript("localStorage.removeItem('token'); localStorage.removeItem('user_info'); localStorage.removeItem('active_live_session_id'); location.reload();") # Added removal of active session id
    ui.navigate.to(f"http://{API_HOST}:{API_PORT}/logout")

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
            # !!! IMPORTANT: Replace with the actual backend endpoint once created !!!
            # This endpoint should check if the user (member/trainer) has a session NOW.
            response = await client.get(f"http://{API_HOST}:{API_PORT}/training/live/sessions/current", headers=headers)
            if response.status_code == 200 and response.json():
                # Optionally store active session ID if returned by the endpoint
                # live_session_id = response.json().get('live_session_id')
                # if live_session_id:
                #    await ui.run_javascript(f"localStorage.setItem('active_live_session_id', '{live_session_id}');")
                return True
            # await ui.run_javascript("localStorage.removeItem('active_live_session_id');")
            return False
    except Exception as e:
        print(f"Error checking active session: {e}")
        # await ui.run_javascript("localStorage.removeItem('active_live_session_id');")
        return False

# --- End Copied Helper Functions ---

async def display_live_dashboard(): # Made async
    # Apply background style
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    ui.query('.nicegui-content').classes('items-center')

    user = await get_current_user()

    # --- Copied Navbar ---
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
        with ui.row().classes('gap-4'):
            ui.button('Home', on_click=lambda: ui.navigate.to('/')).classes('text-white hover:text-blue-300')
            ui.button('Working Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('text-white hover:text-blue-300')
            ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('text-white hover:text-blue-300')
            ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('text-white hover:text-blue-300')
            ui.button('Weekly Schedule', on_click=lambda: ui.navigate.to('/weekly-schedule')).classes('text-white hover:text-blue-300')

            # Conditional Training Preferences Link
            if await is_preference_day():
                 ui.button('Training Preferences', on_click=lambda: ui.navigate.to('/training-preferences')).classes('text-white hover:text-blue-300')

            # Conditional Live Dashboard Link
            if await user_has_active_session(user):
               ui.button('Live Dashboard', on_click=lambda: ui.navigate.to('/live-dashboard')).classes('text-white hover:text-blue-300')

            if user:
                with ui.column():
                    user_button = ui.button(f'👤 {user.get("name", "Account")} ▾').classes('text-white')
                    user_menu = ui.menu().props('auto-close').classes('bg-white text-black shadow-md rounded-md')

                    with user_menu:
                        ui.menu_item('My Profile', on_click=lambda: ui.navigate.to('/myprofile'))
                        ui.menu_item('My Bookings', on_click=lambda: ui.navigate.to('/mybookings'))
                        ui.menu_item('My Plans', on_click=lambda: ui.navigate.to('/mytrainingplans'))
                        ui.menu_item('Logout', on_click=logout)
                    user_button.on('click', user_menu.open)
            else:
                 ui.button('Login/Register', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('text-white hover:text-blue-300')
    # --- End Copied Navbar ---

    # Main content card
    with ui.card().classes('w-full max-w-6xl p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-20'): # Added margin-top and max-width
        ui.label('Live Training Dashboard').classes('text-h4 text-center mb-4 text-blue-300')

        # Container to hold dashboard content
        dashboard_container = ui.column().classes('w-full')
        
        # Get token from local storage
        token_script = '''
        const token = localStorage.getItem('token');
        if (token) {
            return token;
        } else {
            return null;
        }
        '''
        
        # Auto-refresh controls
        auto_refresh_state = ui.state(True)  # Default: enabled
        refresh_rate_state = ui.state(30)  # Default: 30 seconds
        
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('Auto-refresh settings').classes('text-h6')
            
            with ui.row():
                ui.checkbox('Auto-refresh', value=True).bind_value(auto_refresh_state, 'value')
                ui.number(
                    'Refresh rate (seconds)',
                    min=10,
                    max=60,
                    step=5,
                    value=30
                ).bind_value(refresh_rate_state, 'value').props('size=8')
        
        # Placeholder for countdown timer
        refresh_timer_display = ui.label('')
        
        @ui.refreshable
        async def load_dashboard_content():
            # Get token
            token = await ui.run_javascript(token_script)
            if not token:
                ui.notify('Please log in to view the live dashboard', color='negative')
                ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login') # Redirect to login
                return

            # Get user info (already present)
            user_info = await ui.run_javascript('''
                return JSON.parse(localStorage.getItem('user_info') || '{}');
            ''')
            user_type = user_info.get('user_type', '')

            # *** Access Control Check ***
            # Add this check if you want to prevent loading if no session is active NOW
            # has_active = await user_has_active_session(user)
            # if not has_active and user_type != 'manager': # Managers might always see it
            #     dashboard_container.clear()
            #     with dashboard_container:
            #         ui.label("You do not have an active training session right now.").classes('text-info')
            #         ui.button('View Weekly Schedule', on_click=lambda: ui.navigate.to('/weekly-schedule')).props('color=primary')
            #     return

            # Clear and show loading state
            dashboard_container.clear()
            with dashboard_container:
                ui.spinner(size='lg').classes('self-center')
                ui.label('Loading live training data...').classes('self-center')
                
            # Wait a bit to show the loading spinner
            await asyncio.sleep(0.5)
            dashboard_container.clear()
            
            with dashboard_container:
                # Display appropriate dashboard based on user type
                if user_type == "manager":
                    await display_manager_dashboard()
                elif user_type == "trainer":
                    await display_trainer_dashboard()
                elif user_type == "member":
                    await display_member_dashboard()
                else:
                    ui.label("Unauthorized access. Please login with the correct permissions.").classes('text-negative')
        
        async def display_manager_dashboard():
            """Display the manager's view of all active training sessions"""
            ui.label("All Active Training Sessions").classes('text-h5')
            
            try:
                # Get all active sessions
                sessions = await ui.run_javascript(f'''
                    async function getActiveSessions() {{
                        const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/live/sessions/active", {{
                            headers: {{
                                "Authorization": "Bearer " + localStorage.getItem('token')
                            }}
                        }});
                        return await response.json();
                    }}
                    return await getActiveSessions();
                ''')
                
                if not sessions:
                    ui.label("No active training sessions at the moment.").classes('text-info')
                else:
                    # Create a simple table for all active sessions
                    with ui.table().classes('w-full').style('max-height: 300px'):
                        ui.table_head(
                            ui.table_header(
                                ui.table_cell('Session ID'),
                                ui.table_cell('Hall'),
                                ui.table_cell('Trainer'),
                                ui.table_cell('Start Time'),
                                ui.table_cell('Status')
                            )
                        )
                        with ui.table_body():
                            for session in sessions:
                                ui.table_row(
                                    ui.table_cell(session.get('live_session_id', 'N/A')),
                                    ui.table_cell(session.get('hall_name', 'N/A')),
                                    ui.table_cell(session.get('trainer_name', 'N/A')),
                                    ui.table_cell(session.get('start_time', 'N/A')),
                                    ui.table_cell(session.get('status', 'N/A')).classes(
                                        'text-positive' if session.get('status') == 'Completed' else
                                        'text-negative' if session.get('status') == 'Cancelled' else
                                        'text-primary' if session.get('status') == 'In Progress' else
                                        'text-secondary'
                                    )
                                )
                    
                    # Show detailed info for each session in cards
                    ui.label("Session Details").classes('text-h6 q-mt-md')
                    for session in sessions:
                        with ui.card().classes('w-full q-my-sm'):
                            with ui.expansion(f"Session #{session['live_session_id']} in {session['hall_name']} with {session['trainer_name']}"):
                                with ui.row().classes('w-full'):
                                    with ui.column().classes('w-1/2'):
                                        ui.label(f"📍 Hall: {session['hall_name']}")
                                        ui.label(f"👨‍🏫 Trainer: {session['trainer_name']}")
                                        ui.label(f"📊 Status: {session['status']}")
                                        ui.label(f"⏱️ Started at: {session['start_time']}")
                                    
                                    with ui.column().classes('w-1/2 items-end'):
                                        # End session button
                                        ui.button(
                                            "End Session", 
                                            on_click=lambda s=session: end_live_session(s['live_session_id'])
                                        ).props('color=negative')
            
            except Exception as e:
                ui.label(f"Failed to load active sessions: {str(e)}").classes('text-negative')
        
        async def display_trainer_dashboard():
            """Display the trainer's view of their active training sessions"""
            ui.label("Your Active Training Sessions").classes('text-h5')
            
            try:
                # Get trainer's active sessions
                sessions = await ui.run_javascript(f'''
                    async function getTrainerSessions() {{
                        const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/live/sessions/trainer", {{
                            headers: {{
                                "Authorization": "Bearer " + localStorage.getItem('token')
                            }}
                        }});
                        return await response.json();
                    }}
                    return await getTrainerSessions();
                ''')
                
                if not sessions:
                    ui.label("You don't have any active training sessions at the moment.").classes('text-info')
                else:
                    # For each session
                    for session in sessions:
                        with ui.card().classes('w-full q-my-md'):
                            ui.label(f"Session in {session['hall_name']}").classes('text-h6')
                            ui.label(f"⏱️ Started at: {session['start_time']}")
                            ui.label(f"📊 Status: {session['status']}")
                            
                            # Try to get members assigned to this session
                            try:
                                members = await ui.run_javascript(f'''
                                    async function getSessionMembers() {{
                                        const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/schedule/{session['schedule_id']}/members", {{
                                            headers: {{
                                                "Authorization": "Bearer " + localStorage.getItem('token')
                                            }}
                                        }});
                                        return await response.json();
                                    }}
                                    return await getSessionMembers();
                                ''')
                                
                                ui.label("Members").classes('text-subtitle1')
                                
                                if not members:
                                    ui.label("No members assigned to this session.").classes('text-info')
                                else:
                                    # Create a table for members
                                    with ui.table().style('max-height: 200px'):
                                        ui.table_head(
                                            ui.table_header(
                                                ui.table_cell('Name'),
                                                ui.table_cell('Status')
                                            )
                                        )
                                        with ui.table_body():
                                            for member in members:
                                                ui.table_row(
                                                    ui.table_cell(f"{member.get('first_name', '')} {member.get('last_name', '')}"),
                                                    ui.table_cell(member.get('attendance_status', 'N/A')).classes(
                                                        'text-positive' if member.get('attendance_status') == 'Attended' else
                                                        'text-negative' if member.get('attendance_status') == 'No Show' else
                                                        'text-secondary'
                                                    )
                                                )
                            
                            except Exception as e:
                                ui.label(f"Failed to load members: {str(e)}").classes('text-negative')
                            
                            # End session button
                            ui.button(
                                "End Session", 
                                on_click=lambda s=session: end_live_session(s['live_session_id'])
                            ).props('color=negative')
                            
                            ui.separator()
        
            except Exception as e:
                ui.label(f"Failed to load active sessions: {str(e)}").classes('text-negative')
        
        async def display_member_dashboard():
            """Display the member's view of their active training session"""
            ui.label("Your Active Training Session").classes('text-h5')
            
            try:
                # Get member's active sessions
                sessions = await ui.run_javascript(f'''
                    async function getMemberSessions() {{
                        const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/live/sessions/member", {{
                            headers: {{
                                "Authorization": "Bearer " + localStorage.getItem('token')
                            }}
                        }});
                        return await response.json();
                    }}
                    return await getMemberSessions();
                ''')
                
                if not sessions:
                    ui.label("You don't have any active training sessions at the moment.").classes('text-info')
                    
                    # Show link to weekly schedule
                    with ui.card().classes('w-full q-mt-md bg-blue-1'):
                        ui.label("Want to see your upcoming sessions?").classes('text-h6')
                        ui.label("Check your weekly schedule to see your upcoming training sessions.")
                        ui.button('View Weekly Schedule', on_click=lambda: ui.navigate.to('/weekly-schedule')).props('color=primary')
                else:
                    # Should typically be only one active session for a member
                    session = sessions[0]
                    
                    ui.label(f"Session in {session['hall_name']} with {session['trainer_name']}").classes('text-h6')
                    ui.label(f"⏱️ Started at: {session['start_time']}")
                    
                    # Get exercises for this member in this session
                    exercises = await ui.run_javascript(f'''
                        async function getSessionExercises() {{
                            const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/live/sessions/{session['live_session_id']}/exercises", {{
                                headers: {{
                                    "Authorization": "Bearer " + localStorage.getItem('token')
                            }}
                        }});
                        return await response.json();
                    }}
                    return await getSessionExercises();
                    ''')
                    
                    if not exercises:
                        ui.label("No exercises planned for this session. Please check with your trainer.").classes('text-warning')
                    else:
                        ui.label("Your Training Plan").classes('text-h6 q-mt-md')
                        
                        # Display each exercise with progress tracking
                        for i, exercise in enumerate(exercises):
                            with ui.card().classes('w-full q-my-sm'):
                                with ui.expansion(f"{i+1}. {exercise['exercise_name']} {'✓' if exercise['completed'] else ''}"):
                                    with ui.row().classes('w-full'):
                                        with ui.column().classes('w-2/3'):
                                            ui.label(f"Exercise: {exercise['exercise_name']}").classes('text-bold')
                                            ui.label(f"Muscle Group: {exercise['primary_muscle_group']}")
                                            
                                            if exercise['instructions']:
                                                ui.label("Instructions:").classes('text-bold q-mt-sm')
                                                ui.label(exercise['instructions'])
                                            
                                            # Show actual progress
                                            ui.label("Current Progress:").classes('text-bold q-mt-sm')
                                            ui.label(f"Sets Completed: {exercise['sets_completed']}")
                                            ui.label(f"Reps Performed: {exercise['actual_reps'] or 'Not recorded'}")
                                            ui.label(f"Weight Used (kg): {exercise['weight_used'] or 'Not recorded'}")
                                        
                                        with ui.column().classes('w-1/3'):
                                            if exercise['image_url']:
                                                ui.image(exercise['image_url']).classes('w-full')
                                
                                # Only allow updating if not completed
                                if not exercise['completed']:
                                    with ui.card().classes('q-pa-md bg-blue-1'):
                                        ui.label("Update Progress").classes('text-bold')
                                        
                                        # Form for updating progress
                                        with ui.row().classes('w-full items-end'):
                                            with ui.column().classes('w-full'):
                                                sets_input = ui.number('Sets completed', min=0, max=10, value=exercise['sets_completed'] or 0)
                                                reps_input = ui.input('Reps (e.g., "10,8,8")', value=exercise['actual_reps'] or "")
                                                weight_input = ui.input('Weight in kg (e.g., "50,45,40")', value=exercise['weight_used'] or "")
                                                comments_input = ui.textarea('Comments', value=exercise['comments'] or "").classes('w-full')
                                        
                                        with ui.row().classes('q-mt-md justify-between'):
                                            ui.button(
                                                "Save Progress", 
                                                on_click=lambda e=exercise, s=sets_input, r=reps_input, w=weight_input, c=comments_input: 
                                                    update_exercise_progress(
                                                        session['live_session_id'], 
                                                        e['exercise_id'], 
                                                        s.value, 
                                                        r.value, 
                                                        w.value, 
                                                        c.value
                                                    )
                                            ).props('color=primary')
                                            
                                            ui.button(
                                                "Mark as Completed", 
                                                on_click=lambda e=exercise: complete_exercise(
                                                    session['live_session_id'], 
                                                    e['exercise_id']
                                                )
                                            ).props('color=positive')
            except Exception as e:
                ui.label(f"Failed to load active session: {str(e)}").classes('text-negative')
    
    async def update_exercise_progress(live_session_id, exercise_id, sets_completed, actual_reps, weight_used, comments):
        """Update a member's exercise progress in a live session"""
        try:
            progress_data = {
                "sets_completed": sets_completed,
                "actual_reps": actual_reps,
                "weight_used": weight_used,
                "comments": comments
            }
            
            response = await ui.run_javascript(f'''
                async function updateProgress() {{
                    const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/live/sessions/{live_session_id}/progress?exercise_id={exercise_id}", {{
                        method: "POST",
                        headers: {{
                            "Authorization": "Bearer " + localStorage.getItem('token'),
                            "Content-Type": "application/json"
                        }},
                        body: JSON.stringify({json.dumps(progress_data)})
                    }});
                    if (response.ok) {{
                        return await response.json();
                    }} else {{
                        throw new Error("Failed to update progress");
                    }}
                }}
                try {{
                    return await updateProgress();
                }} catch (e) {{
                    return {{ error: e.toString() }};
                }}
            ''')
            
            if response and not response.get("error"):
                ui.notify("Progress updated successfully!", color="positive")
                load_dashboard_content.refresh()
            else:
                ui.notify(f"Failed to update progress: {response.get('error', 'Unknown error')}", color="negative")
        
        except Exception as e:
            ui.notify(f"An error occurred: {str(e)}", color="negative")
    
    async def complete_exercise(live_session_id, exercise_id):
        """Mark an exercise as completed for a member in a live session"""
        try:
            response = await ui.run_javascript(f'''
                async function completeExercise() {{
                    const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/live/sessions/{live_session_id}/complete/{exercise_id}", {{
                        method: "POST",
                        headers: {{
                            "Authorization": "Bearer " + localStorage.getItem('token')
                        }}
                    }});
                    if (response.ok) {{
                        return await response.json();
                    }} else {{
                        throw new Error("Failed to complete exercise");
                    }}
                }}
                try {{
                    return await completeExercise();
                }} catch (e) {{
                    return {{ error: e.toString() }};
                }}
            ''')
            
            if response and not response.get("error"):
                ui.notify("Exercise marked as completed!", color="positive")
                load_dashboard_content.refresh()
            else:
                ui.notify(f"Failed to complete exercise: {response.get('error', 'Unknown error')}", color="negative")
        
        except Exception as e:
            ui.notify(f"An error occurred: {str(e)}", color="negative")
    
    async def end_live_session(live_session_id):
        """End a live training session"""
        try:
            response = await ui.run_javascript(f'''
                async function endSession() {{
                    const response = await fetch("http://{API_HOST}:{API_PORT}/training-plans/live/sessions/{live_session_id}/end", {{
                        method: "POST",
                        headers: {{
                            "Authorization": "Bearer " + localStorage.getItem('token')
                        }}
                    }});
                    if (response.ok) {{
                        return await response.json();
                    }} else {{
                        throw new Error("Failed to end session");
                    }}
                }}
                try {{
                    return await endSession();
                }} catch (e) {{
                    return {{ error: e.toString() }};
                }}
            ''')
            
            if response and not response.get("error"):
                ui.notify("Session ended successfully!", color="positive")
                # Remove from local storage
                await ui.run_javascript('''
                    localStorage.removeItem('active_live_session_id');
                ''')
                load_dashboard_content.refresh()
            else:
                ui.notify(f"Failed to end session: {response.get('error', 'Unknown error')}", color="negative")
        
        except Exception as e:
            ui.notify(f"An error occurred: {str(e)}", color="negative")
    
    # Add refresh button
    with ui.row().classes('q-mt-md'):
        ui.button('Refresh Now', on_click=load_dashboard_content).props('color=primary')
    
    # Initial load
    await load_dashboard_content()
    
    # Remove or keep timer-based auto-refresh
    # async def auto_refresh_timer():
    #    ...
    #    await load_dashboard_content.refresh() # Use await
    #    ...

    # ui.timer(0.1, lambda: asyncio.create_task(auto_refresh_timer()))

# Update ui.py registration:
# ui.page('/live-dashboard')(display_live_dashboard)