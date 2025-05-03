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

async def training_page():
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
    if user:
        # Fetch full user details from the backend
        user = await user_full_details(user)
    print("DEBUG: training_page.py User:", user)
    is_manager = user and user.get("user_type") == "manager"
    is_trainer = user and user.get("user_type") == "trainer"
    is_member = user and user.get("user_type") == "member"

    # Create a layout with sidebar and main content
    with ui.row().classes('w-full p-4 gap-4'):
        # Sidebar for navigation to training features
        with ui.card().classes('w-64 bg-gray-900 rounded-lg shadow-lg'):
            ui.label('Training Features').classes('text-xl font-bold text-center mb-4 text-blue-300')
            
            # Training plans link (current page)
            ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('w-full mb-2 bg-blue-600 text-white')
            
            # Weekly Schedule link
            ui.button('Weekly Schedule', on_click=lambda: ui.navigate.to('/weekly-schedule')).classes('w-full mb-2 bg-gray-800 hover:bg-gray-700 text-white')
            
            # Live Training Dashboard link
            ui.button('Live Training Dashboard', on_click=lambda: ui.navigate.to('/live-dashboard')).classes('w-full mb-2 bg-gray-800 hover:bg-gray-700 text-white')
            
            # Training Preferences link (members only)
            if is_member:
                ui.button('Set Training Preferences', on_click=lambda: ui.navigate.to('/training-preferences')).classes('w-full mb-2 bg-gray-800 hover:bg-gray-700 text-white')
            
            # Helpful information based on user type
            with ui.card().classes('mt-4 p-2 bg-gray-800'):
                if is_member:
                    ui.label('Tips for Members:').classes('font-bold text-blue-300')
                    ui.label('1. Set your weekly training preferences every Thursday').classes('text-sm text-gray-300')
                    ui.label('2. Check the weekly schedule for your assigned sessions').classes('text-sm text-gray-300')
                    ui.label('3. Track your progress in the live dashboard').classes('text-sm text-gray-300')
                elif is_trainer:
                    ui.label('Tips for Trainers:').classes('font-bold text-blue-300')
                    ui.label('1. Start live sessions from the weekly schedule').classes('text-sm text-gray-300')
                    ui.label('2. Monitor member progress in the live dashboard').classes('text-sm text-gray-300')
                elif is_manager:
                    ui.label('Manager Options:').classes('font-bold text-blue-300')
                    ui.label('1. Generate weekly schedules based on preferences').classes('text-sm text-gray-300')
                    ui.label('2. Monitor all active training sessions').classes('text-sm text-gray-300')

        # Main content area
        with ui.card().classes('flex-grow p-6 bg-gray-900 rounded-lg shadow-lg'):
            ui.label('Training Plans').classes('text-2xl font-bold text-center mb-4 text-blue-300')
            response = requests.get("http://127.0.0.1:8000/training-plans")
            plans = response.json() if response.status_code == 200 else []

            if is_manager:
                ui.button('Add a Training Plan', on_click=show_add_training_plan_form).classes('bg-green-500 text-white rounded-full hover:bg-green-600 transition-colors mb-4')

            if plans:
                for plan in plans:
                    with ui.card().classes('mb-2 p-4 bg-gray-800 rounded-lg shadow-md'):
                        ui.label(f"{plan['title']}").classes('text-lg font-bold text-blue-300')
                        ui.label(f"Duration: {plan['duration_weeks']} weeks").classes('text-gray-300')
                        ui.label(f"Focus: {plan['primary_focus']}").classes('text-gray-300')
                        ui.button('View Plan', on_click=lambda: ui.notify(f'Viewing {plan["title"]}')).classes('bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors')
            else:
                ui.label('No training plans available.').classes('text-center text-gray-500')

def show_add_training_plan_form():
    with ui.card().classes('w-96 p-6 bg-white rounded-lg shadow-lg') as form_card:
        ui.label('Add a New Training Plan').classes('text-2xl font-bold text-center mb-4 text-blue-500')

        title = ui.input('Title').classes('mb-2 text-black')
        description = ui.textarea('Description').classes('mb-2 text-black')
        difficulty_level = ui.select(['Beginner', 'Intermediate', 'Advanced', 'All Levels'], label='Difficulty Level').classes('mb-2 text-black')
        duration_weeks = ui.input('Duration (Weeks)').classes('mb-2 text-black')
        days_per_week = ui.input('Days per Week').classes('mb-2 text-black')
        primary_focus = ui.select(['Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'Strength', 'General Fitness'], label='Primary Focus').classes('mb-2 text-black')
        secondary_focus = ui.select(['Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'Strength', 'General Fitness'], label='Secondary Focus (Optional)').classes('mb-2 text-black')
        target_gender = ui.select(['Any', 'Male', 'Female'], label='Target Gender').classes('mb-2 text-black')
        min_age = ui.input('Minimum Age').classes('mb-2 text-black')
        max_age = ui.input('Maximum Age').classes('mb-2 text-black')
        equipment_needed = ui.textarea('Equipment Needed').classes('mb-2 text-black')

        def save_training_plan():
            data = {
                "title": title.value,
                "description": description.value,
                "difficulty_level": difficulty_level.value,
                "duration_weeks": int(duration_weeks.value),
                "days_per_week": int(days_per_week.value),
                "primary_focus": primary_focus.value,
                "secondary_focus": secondary_focus.value if secondary_focus.value else None,
                "target_gender": target_gender.value,
                "min_age": int(min_age.value) if min_age.value else None,
                "max_age": int(max_age.value) if max_age.value else None,
                "equipment_needed": equipment_needed.value,
            }
            response = requests.post(f"http://127.0.0.1:8000/training-plans", json=data)
            if response.status_code == 201:
                ui.notify('Training plan added successfully!', color='green')
                form_card.delete()
                training_page()
            else:
                ui.notify('Failed to add training plan.', color='red')

        def cancel():
            form_card.delete()
            training_page()

        ui.button('Save', on_click=save_training_plan).classes('bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors mr-2')
        ui.button('Cancel', on_click=cancel).classes('bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors')
