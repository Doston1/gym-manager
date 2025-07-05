from nicegui import ui, app
import httpx
from datetime import datetime
from frontend.config import API_HOST, API_PORT
from frontend.components.navbar import create_navbar, apply_page_style, get_current_user

async def full_details():
    # Apply consistent page styling
    apply_page_style()

    async def save_details():
        try:
            token = await ui.run_javascript("localStorage.getItem('token')")
            if not token:
                return
            
            # Get current user to get the user_id
            current_user = await get_current_user()
            if not current_user:
                ui.notify('Unable to get user information', type='error')
                return

            # Combine user and member data
            combined_data = {
                "first_name": first_name.value,
                "last_name": last_name.value,
                "phone": phone.value,
                "date_of_birth": dob.value,
                "gender": gender.value,
                "weight": float(weight.value) if weight.value else None,
                "height": float(height.value) if height.value else None,
                "fitness_goal": fitness_goal.value,
                "fitness_level": fitness_level.value,
                "health_conditions": health_conditions.value
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            async with httpx.AsyncClient() as client:
                # Send combined update request
                response = await client.put(
                    f"http://{API_HOST}:{API_PORT}/users/{current_user['auth_id']}",
                    json=combined_data,
                    headers=headers
                )
                
            if response.status_code == 200:
                ui.notify('Profile updated successfully!', type='positive')
                ui.navigate.to('/')
            else:
                ui.notify('Error updating profile', type='error')
                
        except Exception as e:
            ui.notify(f'Error: {e}', type='error')

    user = await get_current_user()
    if not user:
        ui.navigate.to('/')
        return

    with ui.card().classes('w-full max-w-3xl mx-auto p-6 bg-gray-100 rounded-lg shadow-lg'):
        ui.label('Complete Your Profile').classes('text-2xl font-bold text-center mb-4 text-gray-800')
        ui.label(
            'Please provide your details to help us personalize your experience. '
            'This information helps us provide better service and tailored recommendations.'
        ).classes('text-sm text-center mb-6 text-gray-600')

        with ui.column().classes('w-full gap-4'):
            # Basic user information section
            ui.label('Basic Information').classes('text-xl font-bold text-gray-800 mt-4')
            ui.label(f'Email: {user.get("email", "No email available")}').classes('text-gray-600 mb-2')
            first_name = ui.input('First Name *').classes('w-full bg-white text-gray-800')
            last_name = ui.input('Last Name *').classes('w-full bg-white text-gray-800')
            phone = ui.input('Phone Number *').classes('w-full bg-white text-gray-800')
            dob = ui.input('Date of Birth *').props('type=date').classes('w-full bg-white text-gray-800')
            gender = ui.select(
                ['Male', 'Female', 'Other', 'Prefer not to say'],
                label='Gender *'
            ).classes('w-full bg-white').style('color: #1a1a1a !important')

            # Member specific information section
            ui.label('Fitness Details').classes('text-xl font-bold text-gray-800 mt-4')
            weight = ui.number('Weight (kg) *').classes('w-full bg-white text-gray-800')
            height = ui.number('Height (cm) *').classes('w-full bg-white text-gray-800')
            fitness_goal = ui.select(
                ['Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'General Fitness'],
                label='Fitness Goal *'
            ).classes('w-full bg-white').style('color: #1a1a1a !important')

            fitness_level = ui.select(
                ['Beginner', 'Intermediate', 'Advanced'],
                label='Fitness Level *'
            ).classes('w-full bg-white').style('color: #1a1a1a !important')
            health_conditions = ui.textarea('Health Conditions').classes('w-full bg-white text-gray-800')

            ui.button(
                'Save Details',
                on_click=save_details
            ).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors mt-4')