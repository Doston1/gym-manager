from nicegui import ui
import requests
import httpx
from frontend.config import API_HOST, API_PORT  # Import environment variables

async def get_current_user():
    try:
        token = await ui.run_javascript("localStorage.getItem('token')", timeout=5.0)
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://{API_HOST}:{API_PORT}/me", headers=headers)
                if response.status_code == 200:
                    return response.json()
    except Exception as e:
        print(f"Error fetching current user: {e}")
    return None

async def user_full_details(user):
    # Fetch full user details from the backend
    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["user_id"]}')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching user details: {response.status_code} - {response.text}")
            return None

async def classes_page():
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

    user = await get_current_user()
    if user:
        # Fetch full user details from the backend
        user = await user_full_details(user)
    print("DEBUG: classes_page.py User:", user)
    is_manager = user and user.get("user_type") == "manager"

    # Main content
    with ui.card().classes('w-96 p-6 bg-gray-900 rounded-lg shadow-lg'):
        ui.label('Available Classes').classes('text-2xl font-bold text-center mb-4 text-blue-300')
        response = requests.get("http://127.0.0.1:8000/classes")
        classes = response.json() if response.status_code == 200 else []

        if is_manager:
            ui.button('Add a Class', on_click=show_add_class_form).classes('bg-green-500 text-white rounded-full hover:bg-green-600 transition-colors mb-4')

        if classes:
            for gym_class in classes:
                with ui.card().classes('mb-2 p-4 bg-gray-800 rounded-lg shadow-md'):
                    ui.label(f"{gym_class['name']}").classes('text-lg font-bold text-blue-300')
                    ui.label(f"Trainer: {gym_class['trainer_id']}").classes('text-gray-300')
                    ui.label(f"Time: {gym_class['start_time']} - {gym_class['end_time']}").classes('text-gray-300')
                    ui.button('Register', on_click=lambda: ui.notify(f'Registered for {gym_class["name"]}')).classes('bg-purple-500 text-white rounded-full hover:bg-purple-600 transition-colors')
        else:
            ui.label('No classes available at the moment.').classes('text-center text-gray-500')

def show_add_class_form():
    with ui.card().classes('w-96 p-6 bg-white rounded-lg shadow-lg') as form_card:  # Changed background to white
        ui.label('Add a New Class').classes('text-2xl font-bold text-center mb-4 text-blue-500')  # Adjusted text color

        class_type_id = ui.input('Class Type ID').classes('mb-2 text-black')  # Adjusted input text color
        trainer_id = ui.input('Trainer ID').classes('mb-2 text-black')
        hall_id = ui.input('Hall ID').classes('mb-2 text-black')
        date = ui.input('Date (YYYY-MM-DD)').classes('mb-2 text-black')
        start_time = ui.input('Start Time (HH:MM)').classes('mb-2 text-black')
        end_time = ui.input('End Time (HH:MM)').classes('mb-2 text-black')
        max_participants = ui.input('Max Participants').classes('mb-2 text-black')
        price = ui.input('Price').classes('mb-2 text-black')

        def save_class():
            data = {
                "class_type_id": class_type_id.value,
                "trainer_id": trainer_id.value,
                "hall_id": hall_id.value,
                "date": date.value,
                "start_time": start_time.value,
                "end_time": end_time.value,
                "max_participants": max_participants.value,
                "price": price.value,
            }
            response = requests.post(f"http://127.0.0.1:8000/classes", json=data)
            if response.status_code == 201:
                ui.notify('Class added successfully!', color='green')
                form_card.delete()
                classes_page()
            else:
                ui.notify('Failed to add class.', color='red')

        def cancel():
            form_card.delete()
            classes_page()

        ui.button('Save', on_click=save_class).classes('bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors mr-2')
        ui.button('Cancel', on_click=cancel).classes('bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors')
