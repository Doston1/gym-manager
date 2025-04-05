from nicegui import ui
import requests

def classes_page():
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

    print("In classes_page function")
    with ui.card().classes('w-96 p-6 bg-gray-900 rounded-lg shadow-lg'):
        ui.label('Available Classes').classes('text-2xl font-bold text-center mb-4 text-blue-300')
        response = requests.get("http://127.0.0.1:8000/classes")
        classes = response.json() if response.status_code == 200 else []
        
        if classes:
            for gym_class in classes:
                with ui.card().classes('mb-2 p-4 bg-gray-800 rounded-lg shadow-md'):
                    ui.label(f"{gym_class['name']}").classes('text-lg font-bold text-blue-300')
                    ui.label(f"Trainer: {gym_class['trainer_id']}").classes('text-gray-300')
                    ui.label(f"Time: {gym_class['start_time']} - {gym_class['end_time']}").classes('text-gray-300')
                    ui.button('Register', on_click=lambda: ui.notify(f'Registered for {gym_class["name"]}')).classes('bg-purple-500 text-white rounded-full hover:bg-purple-600 transition-colors')
        else:
            ui.label('No classes available at the moment.').classes('text-center text-gray-500')
