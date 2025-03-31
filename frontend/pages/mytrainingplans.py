from nicegui import ui
import httpx
from frontend.config import API_HOST, API_PORT
from .home_page import get_current_user

async def mytrainingplans_page():
    user = await get_current_user()
    if not user:
        ui.label('You must be logged in to view this page.').classes('text-center text-red-500')
        ui.button('Login', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('bg-blue-500 text-white')
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["user_id"]}/training-plans')
        if response.status_code == 200:
            plans = response.json()
        else:
            plans = []

    with ui.card().classes('w-full p-6'):
        ui.label('My Training Plans').classes('text-3xl font-bold text-center mb-4')

        if plans:
            for plan in plans:
                with ui.card().classes('mb-4 p-4'):
                    ui.label(f'Plan Name: {plan["name"]}').classes('text-lg font-bold')
                    ui.label(f'Description: {plan["description"]}')
                    ui.label(f'Duration: {plan["duration"]} weeks')
        else:
            ui.label('You have no training plans.').classes('text-center text-gray-500')
