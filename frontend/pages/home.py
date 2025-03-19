from nicegui import ui
import requests
from frontend.config import API_HOST, API_PORT  # Import environment variables



# def home_page():
#     with ui.card().classes('w-96 p-6'):
#         ui.label('Welcome to GYMO').classes('text-2xl font-bold text-center mb-4')
#         ui.button('Login', on_click=lambda: ui.navigate.to('/login')).classes('w-full bg-blue-500 text-white mb-2')
#         ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('w-full bg-green-500 text-white mb-2')
#         ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('w-full bg-orange-500 text-white mb-2')

def home_page(user_id: str = None):
    ui.query('.nicegui-content').classes('items-center')

    with ui.card().classes('w-96 p-6'):
        ui.label('Welcome to GYMO').classes('text-2xl font-bold text-center mb-4')

        if user_id:
            # 🔹 Fetch session status
            response = requests.get(f"http://{API_HOST}:{API_PORT}/check-session?user_id={user_id}")
            if response.status_code == 200 and "error" not in response.json():
                user = response.json()
                ui.label(f'Hello, {user.get("name", "User")}!').classes('text-lg text-center mb-2')
                ui.label(f'Email: {user.get("email", "No email")}').classes('text-sm text-center mb-4')
                # ui.button('Protected Page', on_click=lambda: ui.navigate.to(f'/protected?user_id{user_id}')).classes('w-full bg-green-500 text-white mb-2')
                ui.button('Personal Area', on_click=lambda: ui.navigate.to(f'/personal-area?user_id={user_id}')).classes('w-full bg-blue-500 text-white mb-2')
                ui.button('Classes', on_click=lambda: ui.navigate.to(f'/classes?user_id={user_id}')).classes('w-full bg-blue-500 text-white mb-2')
                ui.button('Training Plans', on_click=lambda: ui.navigate(f'/training-plans?user_id={user_id}')).classes('w-full bg-blue-500 text-white mb-2')
                ui.button('Logout', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/logout')).classes('w-full bg-red-500 text-white')
            else:
                ui.label('Session expired. Please log in again.').classes('text-center mb-4')
                ui.button('Login with Auth0', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white')
        else:
            ui.label('Please log in to continue').classes('text-center mb-4')
            ui.button('Login with Auth0', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('w-full bg-blue-500 text-white')
