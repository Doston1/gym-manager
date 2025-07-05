from nicegui import ui
import httpx
from frontend.config import API_HOST, API_PORT
from frontend.components.navbar import create_navbar, apply_page_style

async def mytrainingplans_page():
    # Apply consistent page styling
    apply_page_style()

    # Create navbar and get user
    user = await create_navbar()
    if not user:
        ui.label('You must be logged in to view this page.').classes('text-center text-red-500')
        ui.button('Login', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('bg-blue-500 text-white hover:bg-blue-700')
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["user_id"]}/training-plans')
        if response.status_code == 200:
            plans = response.json()
        else:
            plans = []

    with ui.card().classes('w-full p-6 bg-gray-900 rounded-lg shadow-lg'):
        ui.label('My Training Plans').classes('text-3xl font-bold text-center mb-4 text-blue-300')

        if plans:
            for plan in plans:
                with ui.card().classes('mb-4 p-4 bg-gray-800 rounded-lg shadow-md'):
                    ui.label(f'Plan Name: {plan["name"]}').classes('text-lg font-bold text-blue-300')
                    ui.label(f'Description: {plan["description"]}').classes('text-gray-300')
                    ui.label(f'Duration: {plan["duration"]} weeks').classes('text-gray-300')
                    ui.button('View Details', on_click=lambda: ui.notify(f'Viewing {plan["name"]}')).classes('bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors')
        else:
            ui.label('You have no training plans.').classes('text-center text-gray-500')
