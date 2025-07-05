from nicegui import ui, app
import requests
from frontend.config import API_HOST, API_PORT  # Import environment variables
import httpx
from frontend.components.navbar import create_navbar, apply_page_style, get_current_user, logout

async def home_page(user_id: str = None):
    # Apply consistent page styling
    apply_page_style()

    ui.query('.nicegui-content').classes('items-center')
    
    # Create navbar and get user
    user = await create_navbar()
    if user:
        # Fetch full user details from the backend
        async with httpx.AsyncClient() as client:
            response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["auth_id"]}')
            # print(f"DEBUG: home_page.py user full details response: {response.text}")
            if response.status_code == 200:
                user = response.json()
                if user.get("first_name") == "temp_first_name" and user.get("last_name") == "temp_last_name":
                    # If the user is a temporary user, redirect to full details page
                    ui.navigate.to('/full-details')
                    return
                else:
                    pass
                    # print("DEBUG: in else home_page.py User:", user)

    # print("DEBUG: home_page.py User:", user)

    # Main content
    with ui.card().classes('w-full p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg'):
        if user:
            ui.label(f'Hello, {user.get("first_name", "User")} {user.get("last_name", "")}!').classes('text-lg text-center mb-2')
        else:
            # Welcome message for non-logged-in users
            ui.label('Welcome to Gym Manager').classes('text-4xl font-bold text-center mb-4 text-blue-300')
            ui.label('Your complete solution for managing gym activities, classes, and training plans.').classes('text-lg text-center mb-6 text-gray-300')
            ui.button('Login/Register', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-1/2 bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors mb-6')

        # Three columns for additional options
        with ui.row().classes('gap-8 justify-center'):
            # First column: About & Work Hours
            with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md'):
                ui.label('About & Hours').classes('text-xl font-bold text-center mb-2 text-blue-300')
                ui.label("Learn about our gym's story, location, and check our opening hours.").classes('text-sm text-center mb-4 text-gray-300')
                ui.button('Learn More', on_click=lambda: ui.navigate.to('/about')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors')

            # Second column: Classes
            with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md'):
                ui.label('Classes').classes('text-xl font-bold text-center mb-2 text-blue-300')
                ui.label('Browse and book our wide range of fitness classes led by professional trainers.').classes('text-sm text-center mb-4 text-gray-300')
                ui.button('View Classes', on_click=lambda: ui.navigate.to('/classes')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors')

            # Third column: Training Plans
            with ui.column().classes('w-1/4 bg-gray-800 p-4 rounded-lg shadow-md'):
                ui.label('Training Plans').classes('text-xl font-bold text-center mb-2 text-blue-300')
                ui.label('Discover training plans designed to help you achieve your fitness goals.').classes('text-sm text-center mb-4 text-gray-300')
                ui.button('View Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors')

    

def login():
    auth0_url = f"http://{API_HOST}:{API_PORT}/login"
    ui.navigate.to(auth0_url, new_tab=False)
