from nicegui import ui

def home_page():
    with ui.card().classes('w-96 p-6'):
        ui.label('Welcome to GYMO').classes('text-2xl font-bold text-center mb-4')
        ui.button('Login', on_click=lambda: ui.navigate.to('/login')).classes('w-full bg-blue-500 text-white mb-2')
        ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('w-full bg-green-500 text-white mb-2')
        ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('w-full bg-orange-500 text-white mb-2')
