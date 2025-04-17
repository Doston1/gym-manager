from nicegui import ui, app
import requests
from frontend.config import API_HOST, API_PORT
import httpx
from datetime import datetime

async def working_hours():
    # Apply the same background as home page
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    ui.query('.nicegui-content').classes('items-center')

    # Get current user for navbar
    user = await get_current_user()

    # Navbar
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
        with ui.row().classes('gap-4'):
            ui.button('Home', on_click=lambda: ui.navigate.to('/')).classes('text-white hover:text-blue-300')
            ui.button('Working Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('text-white hover:text-blue-300')
            ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('text-white hover:text-blue-300')
            ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('text-white hover:text-blue-300')
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

    # Get current day (0 = Sunday, 6 = Saturday)
    current_day = datetime.now().weekday()
    # Convert from Monday-based (0-6) to Sunday-based (0-6)
    current_day = (current_day + 1) % 7
    
    # Working hours data - Starting with Sunday
    schedule = [
        {"day": "Sunday", "hours": "08:00 - 20:00"},
        {"day": "Monday", "hours": "06:00 - 22:00"},
        {"day": "Tuesday", "hours": "06:00 - 22:00"},
        {"day": "Wednesday", "hours": "06:00 - 22:00"},
        {"day": "Thursday", "hours": "06:00 - 22:00"},
        {"day": "Friday", "hours": "06:00 - 21:00"},
        {"day": "Saturday", "hours": "08:00 - 20:00"}
    ]

    # Main content
    with ui.card().classes('w-full max-w-7xl mx-auto p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg'):
        ui.label('Gym Working Hours').classes('text-2xl font-bold text-center mb-6 text-blue-300')
        
        with ui.row().classes('w-full justify-between items-center gap-2 overflow-x-auto min-h-[200px] py-8 px-4'):
            for i, day_info in enumerate(schedule):
                is_current = i == current_day
                
                card_classes = 'p-4 rounded-lg shadow-md transition-all duration-300 transform hover:scale-105 flex-shrink-0 w-40'
                if is_current:
                    card_classes += ' bg-cyan-600'  # Only change background for current day
                else:
                    card_classes += ' bg-gray-800'
                
                with ui.card().classes(card_classes):
                    ui.label(day_info["day"]).classes(
                        f'text-center font-bold mb-2 text-lg '
                        f'{"text-white" if is_current else "text-blue-300"}'
                    )
                    ui.label(day_info["hours"]).classes(
                        f'text-center text-base '
                        f'{"text-white" if is_current else "text-gray-300"}'
                    )
                    if is_current:
                        ui.label('(Today)').classes('text-sm text-center mt-2 text-blue-200')

# Add these required functions from home_page.py
def logout():
    ui.run_javascript("localStorage.removeItem('token'); location.reload();")

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
                return response.json()
    except Exception as e:
        print(f"JavaScript Error: {e}")
    return None