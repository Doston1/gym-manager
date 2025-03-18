from nicegui import ui
import requests

def training_page():
    with ui.card().classes('w-96 p-6'):
        ui.label('Training Plans').classes('text-2xl font-bold text-center mb-4')
        response = requests.get("http://127.0.0.1:8000/training-plans")
        plans = response.json() if response.status_code == 200 else []
        
        if plans:
            for plan in plans:
                with ui.card().classes('mb-2 p-4'):
                    ui.label(f"{plan['title']}").classes('text-lg font-bold')
                    ui.label(f"Duration: {plan['duration_weeks']} weeks")
                    ui.label(f"Focus: {plan['primary_focus']}")
                    ui.button('View Plan', on_click=lambda: ui.notify(f'Viewing {plan["title"]}')).classes('bg-blue-500 text-white')
        else:
            ui.label('No training plans available.')
