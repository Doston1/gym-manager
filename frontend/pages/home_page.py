from nicegui import ui, app
import requests
from frontend.config import API_HOST, API_PORT  # Import environment variables
import httpx

async def home_page(user_id: str = None):
    ui.query('.nicegui-content').classes('items-center')
    user = await get_current_user()
    print("DEBUG: home_page.py User:", user)

    # Navbar
    with ui.header().classes('bg-blue-500 text-white p-4 flex justify-between items-center'):
        ui.label('Gym Manager').classes('text-xl font-bold cursor-pointer').on('click', lambda: ui.navigate.to('/'))
        with ui.row().classes('gap-4'):
            ui.button('Home', on_click=lambda: ui.navigate.to('/')).classes('text-white')
            ui.button('Working Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('text-white')
            ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('text-white')
            ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('text-white')
            if user:
                with ui.column():
                    user_button = ui.button(f'👤 {user.get("name", "Account")} ▾').classes('text-white')
                    user_menu = ui.menu().props('auto-close').classes('bg-white text-black shadow-md rounded-md')

                    # with ui.menu():
                    with user_menu:
                        ui.menu_item('My Profile', on_click=lambda: ui.navigate.to('/profile'))
                        ui.menu_item('My Bookings', on_click=lambda: ui.navigate.to('/bookings'))
                        ui.menu_item('My Plans', on_click=lambda: ui.navigate.to('/plans'))
                        ui.menu_item('Logout', on_click=logout)
                    # user_button.on('click', lambda: ui.open_menu(user_button))
                    user_button.on('click', user_menu.open)


    # Main content
    with ui.card().classes('w-full p-6'):
        # if user_id:
        if user:
            ui.label(f'Hello, {user.get("name", "User")}!').classes('text-lg text-center mb-2')
            ui.label(f'Email: {user.get("email", "No email")}').classes('text-sm text-center mb-4')
            ui.button('Personal Area', on_click=lambda: ui.navigate.to(f'/personal-area')).classes('w-full bg-blue-500 text-white mb-2')
        # else:
        #     ui.label('Session expired. Please log in again.').classes('text-center mb-4')
        #     ui.button('Login with Auth0', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white')
        else:
            # Welcome message for non-logged-in users
            ui.label('Welcome to Gym Manager').classes('text-3xl font-bold text-center mb-4')
            ui.label('Your complete solution for managing gym activities, classes, and training plans.').classes('text-lg text-center mb-6')
            ui.button('Login/Register', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-1/2 bg-blue-500 text-white mb-6')
            # ui.button('Login/Register', on_click=login).classes('w-1/2 bg-blue-500 text-white mb-6')

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

    

def login():
    auth0_url = f"http://{API_HOST}:{API_PORT}/login"
    ui.navigate.to(auth0_url, new_tab=False)

def logout():
    ui.run_javascript("localStorage.removeItem('token'); location.reload();")

async def get_current_user():
    try:
        token = await ui.run_javascript(
            "localStorage.getItem('token')",
            timeout=5.0  # increased timeout
        )
        print("DEBUG: home_page.py - get current user = token:", token)
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://{API_HOST}:{API_PORT}/me", headers=headers)
            
            print("DEBUG: /me status:", response.status_code)
            print("DEBUG: /me response:", response.text)

            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"JavaScript Error: {e}")
    return None
