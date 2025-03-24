from nicegui import ui, app
from fastapi import Request
import requests
from frontend.config import API_HOST, API_PORT  # Import environment variables

def home_page(request: Request, user_id: str = None):
    try:
        cookies = request.cookies
        print("DEBUG: home_page.py, cookies:", cookies)
        user_id = request.session.get("user_id")
        print("DEBUG: home_page.py, user_id:", user_id)
        session = requests.Session()
        print("DEBUG: home_page function with user_id:", user_id)
        ui.query('.nicegui-content').classes('items-center')

        response = session.get(f"http://{API_HOST}:{API_PORT}/check-session?user_id={cookies["session"]}")
        
        print("DEBUG: /check-session response:", response.status_code, response.text)
        
        # Check response and parse JSON
        session_data = response.json() if response.status_code == 200 else {}
        is_logged_in = session_data.get("logged_in", False)
        user = session_data.get("user", {})
        print("DEBUG: /check-session session_data:", session_data)
        print("DEBUG: /check-session is_logged_in:", is_logged_in)
        print("DEBUG: /check-session user:", user)

        # Navbar
        with ui.header().classes('bg-blue-500 text-white p-4 flex justify-between items-center'):
            ui.label('Gym Manager').classes('text-xl font-bold cursor-pointer').on('click', lambda: ui.navigate.to('/'))
            with ui.row().classes('gap-4'):
                ui.button('Home', on_click=lambda: ui.navigate.to('/')).classes('text-white')
                ui.button('Working Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('text-white')
                ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('text-white')
                ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('text-white')
                # if user_id:
                if session_data.get("logged_in"):
                    # Dropdown for logged-in user
                    with ui.menu().classes('text-white'):
                        ui.button('My Profile', on_click=lambda: ui.navigate.to(f'/profile?user_id={user_id}'))
                        ui.button('My Bookings', on_click=lambda: ui.navigate.to(f'/bookings?user_id={user_id}'))
                        ui.button('My Plans', on_click=lambda: ui.navigate.to(f'/plans?user_id={user_id}'))
                        ui.button('Logout', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/logout'))

        # Main content
        with ui.card().classes('w-full p-6'):
            # if user_id:
            if session_data.get("logged_in"):
                user=session_data.get("user")
                print("DEBUG: home_page.py User ID:", user_id)
                # Fetch session status
                response = requests.get(f"http://{API_HOST}:{API_PORT}/check-session?user_id={user_id}")
                print("DEBUG:home_page.py, response:", response)
                if response.status_code == 200 and "error" not in response.json():
                    user = response.json()
                    ui.label(f'Hello, {user.get("name", "User")}!').classes('text-lg text-center mb-2')
                    ui.label(f'Email: {user.get("email", "No email")}').classes('text-sm text-center mb-4')
                    ui.button('Personal Area', on_click=lambda: ui.navigate.to(f'/personal-area?user_id={user_id}')).classes('w-full bg-blue-500 text-white mb-2')
                else:
                    ui.label('Session expired. Please log in again.').classes('text-center mb-4')
                    ui.button('Login with Auth0', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white')
            else:
                # Welcome message for non-logged-in users
                ui.label('Welcome to Gym Manager').classes('text-3xl font-bold text-center mb-4')
                ui.label('Your complete solution for managing gym activities, classes, and training plans.').classes('text-lg text-center mb-6')
                ui.button('Login/Register', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-1/2 bg-blue-500 text-white mb-6')

            # Three columns for additional options
            with ui.row().classes('gap-4 justify-center'):
                # First column: Work Hours
                with ui.column().classes('w-1/4'):
                    ui.label('Work Hours').classes('text-xl font-bold text-center mb-2')
                    ui.label("Check our gym's opening and closing times for each day of the week.").classes('text-sm text-center mb-4')
                    ui.button('View Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('w-full bg-blue-500 text-white')

                # Second column: Classes
                with ui.column().classes('w-1/4'):
                    ui.label('Classes').classes('text-xl font-bold text-center mb-2')
                    ui.label('Browse and book our wide range of fitness classes led by professional trainers.').classes('text-sm text-center mb-4')
                    ui.button('View Classes', on_click=lambda: ui.navigate.to('/classes')).classes('w-full bg-blue-500 text-white')

                # Third column: Training Plans
                with ui.column().classes('w-1/4'):
                    ui.label('Training Plans').classes('text-xl font-bold text-center mb-2')
                    ui.label('Discover training plans designed to help you achieve your fitness goals.').classes('text-sm text-center mb-4')
                    ui.button('View Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('w-full bg-blue-500 text-white')
    except requests.RequestException as e:
            print(f"Logout error: {e}")
            ui.notify("Network error during logout", type="negative")
    


# def home_page(user_id: str = None):
#     print("in home_page function with user_id:", user_id)
#     ui.query('.nicegui-content').classes('items-center')
#     print("in home_page function with user_id:", user_id)
#     with ui.card().classes('w-96 p-6'):
#         ui.label('Welcome to GYMO').classes('text-2xl font-bold text-center mb-4')

#         if user_id:
#             print("DEBUG: home_page.py User ID:", user_id)
#             # 🔹 Fetch session status
#             response = requests.get(f"http://{API_HOST}:{API_PORT}/check-session?user_id={user_id}")
#             print("DEBUG:home_page.py, response:", response)
#             if response.status_code == 200 and "error" not in response.json():
#                 user = response.json()
#                 ui.label(f'Hello, {user.get("name", "User")}!').classes('text-lg text-center mb-2')
#                 ui.label(f'Email: {user.get("email", "No email")}').classes('text-sm text-center mb-4')
#                 # ui.button('Protected Page', on_click=lambda: ui.navigate.to.to.to(f'/protected?user_id{user_id}')).classes('w-full bg-green-500 text-white mb-2')
#                 ui.button('Personal Area', on_click=lambda: ui.navigate.to.to.to(f'/personal-area?user_id={user_id}')).classes('w-full bg-blue-500 text-white mb-2')
#                 ui.button('Classes', on_click=lambda: ui.navigate.to.to.to(f'/classes?user_id={user_id}')).classes('w-full bg-blue-500 text-white mb-2')
#                 ui.button('Training Plans', on_click=lambda: ui.navigate.to.to.to(f'/training-plans?user_id={user_id}')).classes('w-full bg-blue-500 text-white mb-2')
#                 ui.button('Logout', on_click=lambda: ui.navigate.to.to.to(f'http://{API_HOST}:{API_PORT}/logout')).classes('w-full bg-red-500 text-white')
#             else:
#                 ui.label('Session expired. Please log in again.').classes('text-center mb-4')
#                 ui.button('Login with Auth0', on_click=lambda: ui.navigate.to.to.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white')
#         else:
#             print("No user ID")
#             ui.label('Please log in to continue').classes('text-center mb-4')
#             ui.button('Login with Auth0', on_click=lambda: ui.navigate.to.to.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white')


