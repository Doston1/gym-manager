from nicegui import ui
from frontend.config import API_HOST, API_PORT
from frontend.utils import api_call, get_current_user_details # Use new utils
import datetime

async def mytrainingplans_page(): # Renamed to my_training_history_page conceptually
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')

    user = await get_current_user_details()
    if not user or user.get("user_type") != "member":
        ui.label('You must be a logged-in member to view training history.').classes('text-center text-red-500 m-auto')
        if not user: ui.button("Login", on_click=lambda: ui.navigate.to(f"http://{API_HOST}:{API_PORT}/login"))
        return

    # --- Navbar (simplified for brevity) ---
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold').on('click', lambda: ui.navigate.to('/'))
        # ... (add other nav buttons) ...

    with ui.card().classes('w-full max-w-4xl p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg mt-4'):
        ui.label('My Training History').classes('text-3xl font-bold text-center mb-6 text-blue-300')

        history_data = await api_call("GET", "/training-history/member")
        
        if not history_data:
            ui.label('No training history found.').classes('text-center text-gray-400')
            return

        # Group history by session (live_session_id or a combination of date and time)
        sessions = {}
        for record in history_data:
            session_id = record.get('live_session_id') # Or construct a unique session identifier
            # session_start_time = record.get('session_start_time', 'Unknown Session Time') # From joined data
            # session_day = record.get('session_day', '') # From joined data
            
            # For robust grouping, ensure your backend /training-history/member returns distinct session info
            # For now, using live_session_id
            if session_id not in sessions:
                # Attempt to parse ISO string and format it
                start_time_str = record.get('created_at', datetime.datetime.utcnow().isoformat()) # Fallback
                try:
                    dt_obj = datetime.datetime.fromisoformat(start_time_str.replace('Z', '+00:00')) # Handle Zulu time
                    formatted_time = dt_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_time = start_time_str # Fallback if parsing fails

                sessions[session_id] = {
                    'time': formatted_time, # This should be the actual session time
                    'exercises': []
                }
            sessions[session_id]['exercises'].append(record)

        sorted_session_ids = sorted(sessions.keys(), key=lambda sid: sessions[sid]['time'], reverse=True)

        for session_id in sorted_session_ids:
            session = sessions[session_id]
            with ui.expansion(f"Session on {session['time']}", icon="event").classes("my-2 w-full"):
                with ui.card_section():
                    if not session['exercises']:
                        ui.label("No exercises recorded for this session.")
                        continue
                    
                    for exercise_log in session['exercises']:
                        with ui.card().classes("w-full p-2 my-1 bg-gray-700"):
                            exercise_name = exercise_log.get('exercise_name', f"Exercise ID: {exercise_log['exercise_id']}")
                            ui.label(f"{exercise_name}").classes("text-lg font-medium")
                            ui.label(f"  Sets Completed: {exercise_log.get('sets_completed', 'N/A')}")
                            ui.label(f"  Actual Reps: {exercise_log.get('actual_reps', 'N/A')}")
                            ui.label(f"  Weight Used: {exercise_log.get('weight_used', 'N/A')}")
                            if exercise_log.get('comments'):
                                ui.label(f"  Comments: {exercise_log.get('comments')}")

# from nicegui import ui
# import httpx
# from frontend.config import API_HOST, API_PORT
# from .home_page import get_current_user

# async def mytrainingplans_page():
#     # Apply a dark blue background across the page
#     ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')

#     # Navbar
#     with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
#         ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
#         with ui.row().classes('gap-4'):
#             ui.button('Home', on_click=lambda: ui.navigate.to('/')).classes('text-white hover:text-blue-300')
#             ui.button('Working Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('text-white hover:text-blue-300')
#             ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('text-white hover:text-blue-300')
#             ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('text-white hover:text-blue-300')

#     user = await get_current_user()
#     if not user:
#         ui.label('You must be logged in to view this page.').classes('text-center text-red-500')
#         ui.button('Login', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('bg-blue-500 text-white hover:bg-blue-700')
#         return

#     async with httpx.AsyncClient() as client:
#         response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["user_id"]}/training-plans')
#         if response.status_code == 200:
#             plans = response.json()
#         else:
#             plans = []

#     with ui.card().classes('w-full p-6 bg-gray-900 rounded-lg shadow-lg'):
#         ui.label('My Training Plans').classes('text-3xl font-bold text-center mb-4 text-blue-300')

#         if plans:
#             for plan in plans:
#                 with ui.card().classes('mb-4 p-4 bg-gray-800 rounded-lg shadow-md'):
#                     ui.label(f'Plan Name: {plan["name"]}').classes('text-lg font-bold text-blue-300')
#                     ui.label(f'Description: {plan["description"]}').classes('text-gray-300')
#                     ui.label(f'Duration: {plan["duration"]} weeks').classes('text-gray-300')
#                     ui.button('View Details', on_click=lambda: ui.notify(f'Viewing {plan["name"]}')).classes('bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors')
#         else:
#             ui.label('You have no training plans.').classes('text-center text-gray-500')
