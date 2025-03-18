from nicegui import ui
import requests

def classes_page():
    with ui.card().classes('w-96 p-6'):
        ui.label('Available Classes').classes('text-2xl font-bold text-center mb-4')
        response = requests.get("http://127.0.0.1:8000/classes")
        classes = response.json() if response.status_code == 200 else []
        
        if classes:
            for gym_class in classes:
                with ui.card().classes('mb-2 p-4'):
                    ui.label(f"{gym_class['name']}").classes('text-lg font-bold')
                    ui.label(f"Trainer: {gym_class['trainer_id']}")
                    ui.label(f"Time: {gym_class['start_time']} - {gym_class['end_time']}")
                    ui.button('Register', on_click=lambda: ui.notify(f'Registered for {gym_class["name"]}')).classes('bg-green-500 text-white')
        else:
            ui.label('No classes available at the moment.')
