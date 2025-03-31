import datetime
from nicegui import ui
import httpx
from frontend.config import API_HOST, API_PORT
from .home_page import get_current_user


async def profile_page():
    user = await get_current_user()
    if not user:
        ui.label('You must be logged in to view this page.').classes('text-center text-red-500')
        ui.button('Login', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('bg-blue-500 text-white')
        return

    with ui.card().classes('w-full p-6'):
        ui.label('My Profile').classes('text-3xl font-bold text-center mb-4')

        # Display user details
        with ui.column().classes('space-y-4'):
            ui.input('First Name', value=user.get('first_name')).bind_value(user, 'first_name')
            ui.input('Last Name', value=user.get('last_name')).bind_value(user, 'last_name')
            ui.input('Email', value=user.get('email')).props('readonly')
            ui.input('Phone', value=user.get('phone')).bind_value(user, 'phone')
            ui.input('Date of Birth', value=user.get('date_of_birth')).bind_value(user, 'date_of_birth')
            ui.select(['Male', 'Female', 'Other'], value=user.get('gender')).bind_value(user, 'gender')

            # Profile image upload
            ui.label('Profile Image').classes('text-lg')
            ui.upload(on_upload=lambda file: upload_profile_image(file, user['user_id'])).props('accept=".jpg,.png"')

        # Save button
        ui.button('Save Changes', on_click=lambda: save_profile(user)).classes('bg-blue-500 text-white')

async def upload_profile_image(file, user_id):
    async with httpx.AsyncClient() as client:
        response = await client.post(f'http://{API_HOST}:{API_PORT}/users/{user_id}/upload-image', files={'file': file})
        if response.status_code == 200:
            ui.notify('Profile image updated successfully!', type='success')
        else:
            ui.notify('Failed to upload image.', type='error')

async def save_profile(user):
    # Filter out unnecessary fields (if needed)
    user_data = {
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "phone": user.get("phone"),
        "date_of_birth": user.get("date_of_birth"),
        "gender": user.get("gender")
    }

    dob = user_data.get("date_of_birth")
    if dob:
        try:
            # If it's a string, parse it
            if isinstance(dob, str):
                dob = datetime.datetime.strptime(dob, "%Y-%m-%d").date()

            # If it's already a date object, convert to string
            if isinstance(dob, datetime.date):
                user_data["date_of_birth"] = dob.isoformat()

        except ValueError:
            ui.notify("Invalid date format. Please use YYYY-MM-DD.", type="error")
            return

    print("DEBUG: User data being sent:", user_data) 

    async with httpx.AsyncClient() as client:
        response = await client.put(f'http://{API_HOST}:{API_PORT}/users/{user["user_id"]}', json=user_data)
        if response.status_code == 200:
            ui.notify('Profile updated successfully!', type='success')
        else:
            ui.notify('Failed to update profile.', type='error')
