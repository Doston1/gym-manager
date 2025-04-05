from nicegui import ui
import requests

def training_page():
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

    with ui.card().classes('w-96 p-6 bg-gray-900 rounded-lg shadow-lg'):
        ui.label('Training Plans').classes('text-2xl font-bold text-center mb-4 text-blue-300')
        response = requests.get("http://127.0.0.1:8000/training-plans")
        plans = response.json() if response.status_code == 200 else []
        
        if plans:
            for plan in plans:
                with ui.card().classes('mb-2 p-4 bg-gray-800 rounded-lg shadow-md'):
                    ui.label(f"{plan['title']}").classes('text-lg font-bold text-blue-300')
                    ui.label(f"Duration: {plan['duration_weeks']} weeks").classes('text-gray-300')
                    ui.label(f"Focus: {plan['primary_focus']}").classes('text-gray-300')
                    ui.button('View Plan', on_click=lambda: ui.notify(f'Viewing {plan["title"]}')).classes('bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors')
        else:
            ui.label('No training plans available.').classes('text-center text-gray-500')
