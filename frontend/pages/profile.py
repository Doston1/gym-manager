import datetime
from nicegui import ui
import httpx
from frontend.config import API_HOST, API_PORT
from frontend.components.navbar import create_navbar, apply_page_style


async def profile_page():
    # Apply consistent page styling
    apply_page_style()
    ui.query('.nicegui-content').classes('items-center')

    # Create navbar and get user
    user = await create_navbar()
    if not user:
        ui.label('You must be logged in to view this page.').classes('text-center text-red-500')
        ui.button('Login', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('bg-blue-500 text-white')
        return
    else:
        # Get from backend the full user object
        async with httpx.AsyncClient() as client:
            response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["auth_id"]}')
            if response.status_code == 200:
                user = response.json()
            else:
                ui.notify('Failed to fetch user data.', type='error')
                return

        with ui.card().classes('w-full max-w-4xl mx-auto p-8 bg-white bg-opacity-95 rounded-lg shadow-xl mt-8'):
            ui.label('My Profile').classes('text-4xl font-bold text-center mb-8 text-gray-800')

            # Basic Information Section
            with ui.card().classes('w-full p-6 mb-6 bg-gray-50 rounded-lg shadow-md'):
                ui.label('Basic Information').classes('text-2xl font-semibold mb-4 text-gray-700')
                
                with ui.grid(columns=2).classes('gap-4 w-full'):
                    ui.input('First Name', value=user.get('first_name')).bind_value(user, 'first_name').classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined')
                    ui.input('Last Name', value=user.get('last_name')).bind_value(user, 'last_name').classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined')
                    ui.input('Email', value=user.get('email')).props('readonly outlined').classes('bg-gray-100 text-gray-600 border border-gray-300 rounded-md p-2')
                    ui.input('Phone', value=user.get('phone')).bind_value(user, 'phone').classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined')
                    ui.input('Date of Birth', value=user.get('date_of_birth')).bind_value(user, 'date_of_birth').classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined type=date')
                    ui.select(['Male', 'Female', 'Other'], value=user.get('gender')).bind_value(user, 'gender').classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined')

                # Profile image upload
                ui.label('Profile Image').classes('text-lg font-medium text-gray-700 mt-4')
                ui.upload(on_upload=lambda file: upload_profile_image(file, user['auth_id'])).props('accept=".jpg,.png"').classes('mt-2')

            # Role-specific sections
            user_type = user.get('user_type', '').lower()
            
            if user_type == 'member' and user.get('member_details'):
                await render_member_section(user)
            elif user_type == 'trainer' and user.get('trainer_details'):
                await render_trainer_section(user)
            elif user_type == 'manager' and user.get('manager_details'):
                await render_manager_section(user)

            # Save button
            ui.button('Save Changes', on_click=lambda: save_profile(user)).classes('bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-colors mt-6')

async def render_member_section(user):
    """Render member-specific fields"""
    member_details = user.get('member_details', {})
    
    with ui.card().classes('w-full p-6 mb-6 bg-green-50 rounded-lg shadow-md'):
        ui.label('Member Information').classes('text-2xl font-semibold mb-4 text-green-700')
        
        with ui.grid(columns=2).classes('gap-4 w-full'):
            weight_input = ui.input('Weight (kg)', value=member_details.get('weight')).classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined type=number')
            height_input = ui.input('Height (cm)', value=member_details.get('height')).classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined type=number')
            
            fitness_goal_input = ui.input('Fitness Goal', value=member_details.get('fitness_goal')).classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined')
            fitness_level_select = ui.select(['Beginner', 'Intermediate', 'Advanced'], value=member_details.get('fitness_level')).classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined')
            
        health_conditions_input = ui.textarea('Health Conditions', value=member_details.get('health_conditions')).classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2 w-full mt-4').props('outlined')
        
        # Store references to the inputs for later use
        if 'member_details' not in user:
            user['member_details'] = {}
        
        # Bind values to user object
        weight_input.bind_value(user['member_details'], 'weight')
        height_input.bind_value(user['member_details'], 'height')
        fitness_goal_input.bind_value(user['member_details'], 'fitness_goal')
        fitness_level_select.bind_value(user['member_details'], 'fitness_level')
        health_conditions_input.bind_value(user['member_details'], 'health_conditions')


async def render_trainer_section(user):
    """Render trainer-specific fields"""
    trainer_details = user.get('trainer_details', {})
    
    with ui.card().classes('w-full p-6 mb-6 bg-blue-50 rounded-lg shadow-md'):
        ui.label('Trainer Information').classes('text-2xl font-semibold mb-4 text-blue-700')
        
        with ui.grid(columns=2).classes('gap-4 w-full'):
            specialization_input = ui.input('Specialization', value=trainer_details.get('specialization')).classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined')
            years_exp_input = ui.input('Years of Experience', value=trainer_details.get('years_of_experience')).classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined type=number')
            
        bio_input = ui.textarea('Bio', value=trainer_details.get('bio')).classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2 w-full mt-4').props('outlined')
        certifications_input = ui.textarea('Certifications', value=trainer_details.get('certifications')).classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2 w-full mt-4').props('outlined')
        
        # Store references to the inputs for later use
        if 'trainer_details' not in user:
            user['trainer_details'] = {}
        
        # Bind values to user object
        specialization_input.bind_value(user['trainer_details'], 'specialization')
        years_exp_input.bind_value(user['trainer_details'], 'years_of_experience')
        bio_input.bind_value(user['trainer_details'], 'bio')
        certifications_input.bind_value(user['trainer_details'], 'certifications')


async def render_manager_section(user):
    """Render manager-specific fields"""
    manager_details = user.get('manager_details', {})
    
    with ui.card().classes('w-full p-6 mb-6 bg-purple-50 rounded-lg shadow-md'):
        ui.label('Manager Information').classes('text-2xl font-semibold mb-4 text-purple-700')
        
        with ui.grid(columns=2).classes('gap-4 w-full'):
            department_input = ui.input('Department', value=manager_details.get('department')).classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined')
            hire_date_input = ui.input('Hire Date', value=manager_details.get('hire_date')).classes('bg-white text-gray-800 border border-gray-300 rounded-md p-2').props('outlined type=date')
            
        # Store references to the inputs for later use
        if 'manager_details' not in user:
            user['manager_details'] = {}
        
        # Bind values to user object
        department_input.bind_value(user['manager_details'], 'department')
        hire_date_input.bind_value(user['manager_details'], 'hire_date')


async def upload_profile_image(file, auth_id):
    async with httpx.AsyncClient() as client:
        response = await client.post(f'http://{API_HOST}:{API_PORT}/users/{auth_id}/upload-image', files={'file': file})
        if response.status_code == 200:
            ui.notify('Profile image updated successfully!', type='success')
        else:
            ui.notify('Failed to upload image.', type='error')


async def save_profile(user):
    # Prepare the data to be sent to the backend
    update_data = {
        # Basic user fields
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "phone": user.get("phone"),
        "date_of_birth": user.get("date_of_birth"),
        "gender": user.get("gender")
    }

    # Handle date of birth formatting
    dob = update_data.get("date_of_birth")
    if dob:
        try:
            # If it's a string, parse it
            if isinstance(dob, str):
                dob = datetime.datetime.strptime(dob, "%Y-%m-%d").date()

            # If it's already a date object, convert to string
            if isinstance(dob, datetime.date):
                update_data["date_of_birth"] = dob.isoformat()

        except ValueError:
            ui.notify("Invalid date format. Please use YYYY-MM-DD.", type="error")
            return

    # Add role-specific data
    user_type = user.get('user_type', '').lower()
    
    if user_type == 'member' and user.get('member_details'):
        member_details = user['member_details']
        update_data.update({
            "weight": member_details.get('weight'),
            "height": member_details.get('height'),
            "fitness_goal": member_details.get('fitness_goal'),
            "fitness_level": member_details.get('fitness_level'),
            "health_conditions": member_details.get('health_conditions')
        })
    elif user_type == 'trainer' and user.get('trainer_details'):
        trainer_details = user['trainer_details']
        update_data.update({
            "specialization": trainer_details.get('specialization'),
            "bio": trainer_details.get('bio'),
            "certifications": trainer_details.get('certifications'),
            "years_of_experience": trainer_details.get('years_of_experience')
        })
    elif user_type == 'manager' and user.get('manager_details'):
        manager_details = user['manager_details']
        update_data.update({
            "department": manager_details.get('department'),
            "hire_date": manager_details.get('hire_date')
        })

    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}

    print("DEBUG: User data being sent:", update_data) 

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(f'http://{API_HOST}:{API_PORT}/users/{user["auth_id"]}', json=update_data)
            if response.status_code == 200:
                ui.notify('Profile updated successfully!', type='positive')
                # Refresh the page to show updated data
                ui.navigate.to('/myprofile')
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                ui.notify(f'Failed to update profile: {error_detail}', type='negative')
    except Exception as e:
        ui.notify(f'Error updating profile: {str(e)}', type='negative')
