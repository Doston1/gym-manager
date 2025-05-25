from datetime import datetime
from nicegui import ui, app
from frontend.config import API_HOST, API_PORT
from frontend.utils import api_call, get_current_user_details # Import new utils
import asyncio # For sleep

async def home_page():
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    ui.query('.nicegui-content').classes('items-center')

    user = await get_current_user_details() # Use the new utility

    if user and user.get("first_name") == "temp_first_name":
        ui.navigate.to('/full-details')
        return

    print("DEBUG: home_page.py User:", user)

    # Navbar
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
        with ui.row().classes('gap-4 items-center'): # Added items-center
            ui.button('Home', on_click=lambda: ui.navigate.to('/')).props('flat color=white')
            ui.button('Working Hours', on_click=lambda: ui.navigate.to('/work-hours')).props('flat color=white')
            ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).props('flat color=white')
            ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).props('flat color=white')
            ui.button('Weekly Schedule', on_click=lambda: ui.navigate.to('/weekly-schedule')).props('flat color=white')

            is_thursday = datetime.date.today().weekday() == 3 # Thursday
            if user and user.get("user_type") == "member" and is_thursday:
                 ui.button('Set Preferences', on_click=lambda: ui.navigate.to('/training-preferences')).props('flat color=white icon=event')

            # Check for active live session (member or trainer)
            live_session_button_placeholder = ui.row() # Placeholder for the button

            async def check_and_show_live_button():
                live_session_button_placeholder.clear()
                active_session = None
                if user:
                    if user.get("user_type") == "member":
                        active_session = await api_call("GET", "/live-sessions/active/member")
                    elif user.get("user_type") == "trainer":
                        active_session = await api_call("GET", "/live-sessions/active/trainer")
                    # Managers might see a different kind of live overview, not a single "Live Training" button for themselves.
                
                if active_session: # active_session will be the session object or None
                    with live_session_button_placeholder:
                        ui.button('Live Training', on_click=lambda: ui.navigate.to('/live-dashboard')).props('flat color=red icon=fitness_center')
            
            await check_and_show_live_button() # Initial check
            # ui.timer(30.0, check_and_show_live_button, once=False) # Optionally, periodically check

            if user:
                with ui.dropdown_button(f'👤 {user.get("first_name", "Account")}', auto_close=True).props('flat color=white'):
                    ui.menu_item('My Profile', on_click=lambda: ui.navigate.to('/myprofile'))
                    if user.get("user_type") == "member":
                        ui.menu_item('My Bookings (Classes)', on_click=lambda: ui.navigate.to('/mybookings'))
                        ui.menu_item('My Training History', on_click=lambda: ui.navigate.to('/mytrainingplans'))
                    ui.menu_item('Logout', on_click=logout)
            else:
                ui.button('Login', on_click=login).props('flat color=white')
                
    # Main content (as before)
    with ui.card().classes('w-full p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg'):
        if not user:
            ui.label('Welcome to Gym Manager').classes('text-4xl font-bold text-center mb-4 text-blue-300')
            ui.label('Your complete solution for managing gym activities, classes, and training plans.').classes('text-lg text-center mb-6 text-gray-300')
            ui.button('Login/Register', on_click=login).classes('w-1/2 bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors mb-6')
        else:
            ui.label(f'Welcome back, {user.get("first_name", "User")}!').classes('text-2xl font-bold text-center mb-6 text-blue-300')

        with ui.row().classes('gap-8 justify-center mt-6'):
            # Columns as before
            with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md items-center'):
                ui.icon('schedule', size='lg').classes('text-cyan-400 mb-2')
                ui.label('Work Hours').classes('text-xl font-bold text-center mb-2 text-blue-300')
                ui.button('View Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600')

            with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md items-center'):
                ui.icon('groups', size='lg').classes('text-cyan-400 mb-2')
                ui.label('Classes').classes('text-xl font-bold text-center mb-2 text-blue-300')
                ui.button('View Classes', on_click=lambda: ui.navigate.to('/classes')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600')

            with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md items-center'):
                ui.icon('fitness_center', size='lg').classes('text-cyan-400 mb-2')
                ui.label('Training Plans').classes('text-xl font-bold text-center mb-2 text-blue-300')
                ui.button('View Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600')

def login():
    # The /login route on backend redirects to Auth0
    ui.navigate.to(f"http://{API_HOST}:{API_PORT}/login", new_tab=False)

def logout():
    # Clear local token and redirect to backend logout which handles Auth0
    ui.run_javascript("localStorage.removeItem('token'); localStorage.removeItem('user_info');")
    ui.navigate.to(f"http://{API_HOST}:{API_PORT}/logout", new_tab=False)
    # A full page reload might be needed after logout to clear state
    # ui.navigate.to('/', new_tab=False, force_reload=True) # Consider after Auth0 redirect



# ============ OLD VERSION ============
# from nicegui import ui, app
# import requests
# from frontend.config import API_HOST, API_PORT  # Import environment variables
# import httpx

# async def home_page(user_id: str = None):
#     # Apply a dark blue background across the page
#     ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')

#     ui.query('.nicegui-content').classes('items-center')
#     user = await get_current_user()
#     if user:
#         # Fetch full user details from the backend
#         async with httpx.AsyncClient() as client:
#             response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["user_id"]}')
#             if response.status_code == 200:
#                 user = response.json()
#                 if user.get("first_name") == "temp_first_name" and user.get("last_name") == "temp_last_name":
#                     # If the user is a temporary user, redirect to full details page
#                     ui.navigate.to('/full-details')
#                     return

#     print("DEBUG: home_page.py User:", user)

#     # Navbar
#     with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
#         ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
#         with ui.row().classes('gap-4'):
#             ui.button('Home', on_click=lambda: ui.navigate.to('/')).classes('text-white hover:text-blue-300')
#             ui.button('Working Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('text-white hover:text-blue-300')
#             ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('text-white hover:text-blue-300')
#             ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('text-white hover:text-blue-300')
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


#     # Main content
#     with ui.card().classes('w-full p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg'):
#         if user:
#             ui.label(f'Hello, {user.get("first_name", "User")} {user.get("last_name", "")}!').classes('text-lg text-center mb-2')
#         else:
#             # Welcome message for non-logged-in users
#             ui.label('Welcome to Gym Manager').classes('text-4xl font-bold text-center mb-4 text-blue-300')
#             ui.label('Your complete solution for managing gym activities, classes, and training plans.').classes('text-lg text-center mb-6 text-gray-300')
#             ui.button('Login/Register', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-1/2 bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors mb-6')

#         # Three columns for additional options
#         with ui.row().classes('gap-8 justify-center'):
#             # First column: Work Hours
#             with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md'):
#                 ui.label('Work Hours').classes('text-xl font-bold text-center mb-2 text-blue-300')
#                 ui.label("Check our gym's opening and closing times for each day of the week.").classes('text-sm text-center mb-4 text-gray-300')
#                 ui.button('View Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors')

#             # Second column: Classes
#             with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md'):
#                 ui.label('Classes').classes('text-xl font-bold text-center mb-2 text-blue-300')
#                 ui.label('Browse and book our wide range of fitness classes led by professional trainers.').classes('text-sm text-center mb-4 text-gray-300')
#                 ui.button('View Classes', on_click=lambda: ui.navigate.to('/classes')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors')

#             # Third column: Training Plans
#             with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md'):
#                 ui.label('Training Plans').classes('text-xl font-bold text-center mb-2 text-blue-300')
#                 ui.label('Discover training plans designed to help you achieve your fitness goals.').classes('text-sm text-center mb-4 text-gray-300')
#                 ui.button('View Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors')

    

# def login():
#     auth0_url = f"http://{API_HOST}:{API_PORT}/login"
#     ui.navigate.to(auth0_url, new_tab=False)

# def logout():
#     ui.run_javascript("localStorage.removeItem('token'); location.reload();")
#     ui.navigate.to(f"http://{API_HOST}:{API_PORT}/logout")

# async def get_current_user():
#     try:
#         token = await ui.run_javascript(
#             "localStorage.getItem('token')",
#             timeout=5.0  # increased timeout
#         )
#         print("DEBUG: home_page.py - get current user = token:", token)
#         if token:
#             headers = {"Authorization": f"Bearer {token}"}
#             async with httpx.AsyncClient() as client:
#                 response = await client.get(f"http://{API_HOST}:{API_PORT}/me", headers=headers)
            
#             print("DEBUG: /me status:", response.status_code)
#             print("DEBUG: /me response:", response.text)

#             if response.status_code == 200:
#                 return response.json()
#     except Exception as e:
#         print(f"JavaScript Error: {e}")
#     return None
