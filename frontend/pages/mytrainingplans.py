from nicegui import ui
import httpx
from frontend.config import API_HOST, API_PORT
from .home_page import get_current_user

async def mytrainingplans_page():
    # Apply a dark blue background across the page
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')

    # Navbar
    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
        with ui.row().classes('gap-4'):
            ui.button('Home', on_click=lambda: ui.navigate.to('/')).classes('text-white hover:text-blue-300')
            ui.button('Working Hours', on_click=lambda: ui.navigate.to('/work-hours')).classes('text-white hover:text-blue-300')
            ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('text-white hover:text-blue-300')
            ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('text-white hover:text-blue-300')

    user = await get_current_user()
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
