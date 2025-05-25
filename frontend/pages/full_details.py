
# frontend/pages/full_details.py
from nicegui import ui, app
import httpx
from datetime import datetime
from frontend.config import API_HOST, API_PORT

async def full_details():
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    
    # This function fetches the currently logged-in user's basic info from /me
    async def get_auth_user_info():
        try:
            token = await ui.run_javascript("localStorage.getItem('token')", timeout=5.0)
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"http://{API_HOST}:{API_PORT}/me", headers=headers) # Call /me
                if response.status_code == 200:
                    return response.json() # Contains firebase_uid, email, user_type, db_user_id, member_id etc.
        except Exception as e:
            print(f"Error fetching auth user info: {e}")
        return None

    # This function fetches detailed user profile from /users/{db_user_id}
    async def get_user_profile(db_user_id: int):
        try:
            token = await ui.run_javascript("localStorage.getItem('token')", timeout=5.0)
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                async with httpx.AsyncClient() as client:
                    # Use the DB user_id to fetch full profile
                    response = await client.get(f"http://{API_HOST}:{API_PORT}/users/{db_user_id}", headers=headers)
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            print(f"Error fetching user profile: {e}")
        return None


    async def save_details(user_data_to_save, member_data_to_save):
        try:
            token = await ui.run_javascript("localStorage.getItem('token')")
            if not token:
                ui.notify('Authentication token not found. Please log in.', type='error')
                return

            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            
            # Combine data for the PUT request payload to /users/me/profile
            # The endpoint expects two Pydantic models, so we send them as top-level keys
            # However, FastAPI can also take them as a single JSON body if UserUpdate and MemberUpdate are part of a larger model
            # For now, let's assume the endpoint /users/me/profile takes UserUpdate and MemberUpdate as separate query/body params or a combined model.
            # The current backend route is:
            # async def update_my_profile(user_update_data: UserUpdate, member_update_data: MemberUpdate = None, ...)
            # This means FastAPI will expect 'user_update_data' and 'member_update_data' in the request.
            # If sent as a single JSON, FastAPI needs to be configured or the model structured to handle it.
            # Let's send as a single JSON object and adjust backend if needed, or send as multipart/form-data, or two JSON parts.
            # Simplest might be to send one JSON object that the backend route can parse.
            # Let's assume the backend `update_my_profile` expects a JSON body where `user_update_data` and `member_update_data` are keys.
            # This is not standard for Pydantic models as separate args.
            # A common way is to have a single Pydantic model for the request body.
            
            # Let's try sending it as one JSON payload and see if backend can handle it with `request.json()`
            # The backend PUT /users/{user_id} was doing `await request.json()`
            # The new PUT /users/me/profile uses Pydantic models directly in args.
            # So, we need to structure the payload to match.
            # This means we cannot just send one flat JSON.
            # We'll construct the payload so that it matches the Pydantic models.

            payload = {}
            if user_data_to_save:
                payload.update(user_data_to_save) # user_update_data fields
            if member_data_to_save:
                 payload.update(member_data_to_save) # member_update_data fields
            
            # It's more robust if the frontend sends what the backend expects directly.
            # The backend endpoint `update_my_profile` expects `user_update_data: UserUpdate` and `member_update_data: MemberUpdate`.
            # This means we need to send a JSON that can be parsed into these.
            # If FastAPI parses UserUpdate from the body, how does it get MemberUpdate?
            # Usually, you'd have one combined Pydantic model for the request body.
            # class ProfileUpdatePayload(BaseModel):
            #     user_details: UserUpdate
            #     member_details: Optional[MemberUpdate]
            # Or, send UserUpdate as body, and MemberUpdate as query params (not ideal for larger data).

            # Let's adjust the backend `update_my_profile` to accept a single payload model.
            # (Will do this after this frontend part) - For now, assuming it can take flat JSON for both.

            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"http://{API_HOST}:{API_PORT}/users/me/profile", # Correct endpoint
                    json=payload, # Send combined data
                    headers=headers
                )
                
            if response.status_code == 200:
                ui.notify('Profile updated successfully!', type='positive')
                # Update local user info if possible, or trigger a refresh of it.
                await ui.run_javascript("localStorage.removeItem('user_info');") # Force refresh on next get_current_user
                ui.navigate.to('/')
            else:
                error_detail = response.json().get("detail", "Unknown error")
                ui.notify(f'Error updating profile: {error_detail} (Status: {response.status_code})', type='error')
                
        except Exception as e:
            ui.notify(f'An unexpected error occurred: {e}', type='error')

    auth_user = await get_auth_user_info()
    if not auth_user:
        ui.notify('Could not retrieve user information. Please log in again.', type='error')
        ui.navigate.to('/') # Or login page
        return

    # Fetch the full current profile data to pre-fill the form
    # This user object contains current values from DB
    user_profile = await get_user_profile(auth_user.get("user_id")) 
    if not user_profile:
        ui.notify('Could not load full profile data. Using basic info.', type='warning')
        # Fallback to auth_user if full profile fails, though this shouldn't happen for logged-in user
        user_profile = auth_user 


    with ui.card().classes('w-full max-w-3xl mx-auto p-6 bg-gray-100 rounded-lg shadow-lg text-black'): # Ensure text is black for inputs
        ui.label('Complete Your Profile').classes('text-2xl font-bold text-center mb-4 text-gray-800')
        ui.label(
            'Please provide your details to help us personalize your experience. '
            'This information helps us provide better service and tailored recommendations.'
        ).classes('text-sm text-center mb-6 text-gray-600')

        # Prepare dictionaries to hold form values
        # Pre-fill with data from user_profile
        user_form_data = {
            "first_name": user_profile.get("first_name", ""),
            "last_name": user_profile.get("last_name", ""),
            "phone": user_profile.get("phone", ""),
            "date_of_birth": user_profile.get("date_of_birth", ""), # Ensure YYYY-MM-DD format
            "gender": user_profile.get("gender", "Prefer not to say"),
        }
        member_form_data = {
            "weight": user_profile.get("member", {}).get("weight") if user_profile.get("user_type") == "member" else None,
            "height": user_profile.get("member", {}).get("height") if user_profile.get("user_type") == "member" else None,
            "fitness_goal": user_profile.get("member", {}).get("fitness_goal") if user_profile.get("user_type") == "member" else "General Fitness",
            "fitness_level": user_profile.get("member", {}).get("fitness_level") if user_profile.get("user_type") == "member" else "Beginner",
            "health_conditions": user_profile.get("member", {}).get("health_conditions") if user_profile.get("user_type") == "member" else "",
        }


        with ui.column().classes('w-full gap-4'):
            ui.label('Basic Information').classes('text-xl font-bold text-gray-800 mt-4')
            ui.label(f'Email: {user_profile.get("email", "No email available")}').classes('text-gray-600 mb-2')
            
            first_name_input = ui.input('First Name *', value=user_form_data["first_name"]).classes('w-full bg-white text-gray-800')
            last_name_input = ui.input('Last Name *', value=user_form_data["last_name"]).classes('w-full bg-white text-gray-800')
            phone_input = ui.input('Phone Number', value=user_form_data["phone"]).classes('w-full bg-white text-gray-800')
            
            # Date of Birth: Ensure value is in YYYY-MM-DD for the date input
            dob_value = user_form_data["date_of_birth"]
            if dob_value and not isinstance(dob_value, str): # If it's a date object
                 dob_value = dob_value.isoformat()

            dob_input = ui.input('Date of Birth', value=dob_value).props('type=date').classes('w-full bg-white text-gray-800')
            
            gender_select = ui.select(
                ['Male', 'Female', 'Other', 'Prefer not to say'],
                label='Gender',
                value=user_form_data["gender"]
            ).classes('w-full bg-white').style('color: #333 !important; .q-field__native: { color: #333 !important; }')


            if auth_user.get("user_type") == "member":
                ui.label('Fitness Details').classes('text-xl font-bold text-gray-800 mt-4')
                weight_input = ui.number('Weight (kg)', value=member_form_data["weight"], format='%.1f').classes('w-full bg-white text-gray-800')
                height_input = ui.number('Height (cm)', value=member_form_data["height"], format='%.1f').classes('w-full bg-white text-gray-800')
                
                fitness_goal_select = ui.select(
                    ['Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'General Fitness'],
                    label='Fitness Goal',
                    value=member_form_data["fitness_goal"]
                ).classes('w-full bg-white').style('color: #333 !important;')

                fitness_level_select = ui.select(
                    ['Beginner', 'Intermediate', 'Advanced'],
                    label='Fitness Level',
                    value=member_form_data["fitness_level"]
                ).classes('w-full bg-white').style('color: #333 !important;')
                health_conditions_input = ui.textarea('Health Conditions', value=member_form_data["health_conditions"]).classes('w-full bg-white text-gray-800')

            async def handle_save():
                # Collect data from inputs
                user_data_payload = {
                    "first_name": first_name_input.value,
                    "last_name": last_name_input.value,
                    "phone": phone_input.value or None, # Ensure None if empty
                    "date_of_birth": dob_input.value or None,
                    "gender": gender_select.value or None,
                }
                # Filter out None values, but allow empty strings if that's intended (e.g. for phone)
                user_data_payload = {k: v for k, v in user_data_payload.items() if v is not None}


                member_data_payload = {}
                if auth_user.get("user_type") == "member":
                    member_data_payload = {
                        "weight": float(weight_input.value) if weight_input.value is not None else None,
                        "height": float(height_input.value) if height_input.value is not None else None,
                        "fitness_goal": fitness_goal_select.value or None,
                        "fitness_level": fitness_level_select.value or None,
                        "health_conditions": health_conditions_input.value or None,
                    }
                    member_data_payload = {k: v for k, v in member_data_payload.items() if v is not None}
                
                # Call the save_details function
                await save_details(user_data_payload, member_data_payload if member_data_payload else None)

            ui.button(
                'Save Details',
                on_click=handle_save
            ).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors mt-4')

# ----------------------------------
# from nicegui import ui, app
# import httpx
# from datetime import datetime
# from frontend.config import API_HOST, API_PORT

# async def full_details():
#     # Apply same styling as home page
#     ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
    
#     async def get_current_user():
#         try:
#             token = await ui.run_javascript("localStorage.getItem('token')", timeout=5.0)  # increased timeout
#             if token:
#                 headers = {"Authorization": f"Bearer {token}"}
#                 async with httpx.AsyncClient() as client:
#                     response = await client.get(f"http://{API_HOST}:{API_PORT}/me", headers=headers)
#                 if response.status_code == 200:
#                     return response.json()
#         except Exception as e:
#             print(f"Error: {e}")
#         return None

#     async def save_details():
#         try:
#             token = await ui.run_javascript("localStorage.getItem('token')")
#             if not token:
#                 return
            
#             # Get current user to get the user_id
#             current_user = await get_current_user()
#             if not current_user:
#                 ui.notify('Unable to get user information', type='error')
#                 return

#             # Combine user and member data
#             combined_data = {
#                 "first_name": first_name.value,
#                 "last_name": last_name.value,
#                 "phone": phone.value,
#                 "date_of_birth": dob.value,
#                 "gender": gender.value,
#                 "weight": float(weight.value) if weight.value else None,
#                 "height": float(height.value) if height.value else None,
#                 "fitness_goal": fitness_goal.value,
#                 "fitness_level": fitness_level.value,
#                 "health_conditions": health_conditions.value
#             }
            
#             headers = {"Authorization": f"Bearer {token}"}
#             async with httpx.AsyncClient() as client:
#                 # Send combined update request
#                 response = await client.put(
#                     f"http://{API_HOST}:{API_PORT}/users/{current_user['user_id']}",
#                     json=combined_data,
#                     headers=headers
#                 )
                
#             if response.status_code == 200:
#                 ui.notify('Profile updated successfully!', type='positive')
#                 ui.navigate.to('/')
#             else:
#                 ui.notify('Error updating profile', type='error')
                
#         except Exception as e:
#             ui.notify(f'Error: {e}', type='error')

#     user = await get_current_user()
#     if not user:
#         ui.navigate.to('/')
#         return

#     with ui.card().classes('w-full max-w-3xl mx-auto p-6 bg-gray-100 rounded-lg shadow-lg'):
#         ui.label('Complete Your Profile').classes('text-2xl font-bold text-center mb-4 text-gray-800')
#         ui.label(
#             'Please provide your details to help us personalize your experience. '
#             'This information helps us provide better service and tailored recommendations.'
#         ).classes('text-sm text-center mb-6 text-gray-600')

#         with ui.column().classes('w-full gap-4'):
#             # Basic user information section
#             ui.label('Basic Information').classes('text-xl font-bold text-gray-800 mt-4')
#             ui.label(f'Email: {user.get("email", "No email available")}').classes('text-gray-600 mb-2')
#             first_name = ui.input('First Name *').classes('w-full bg-white text-gray-800')
#             last_name = ui.input('Last Name *').classes('w-full bg-white text-gray-800')
#             phone = ui.input('Phone Number *').classes('w-full bg-white text-gray-800')
#             dob = ui.input('Date of Birth *').props('type=date').classes('w-full bg-white text-gray-800')
#             gender = ui.select(
#                 ['Male', 'Female', 'Other', 'Prefer not to say'],
#                 label='Gender *'
#             ).classes('w-full bg-white').style('color: #1a1a1a !important')

#             # Member specific information section
#             ui.label('Fitness Details').classes('text-xl font-bold text-gray-800 mt-4')
#             weight = ui.number('Weight (kg) *').classes('w-full bg-white text-gray-800')
#             height = ui.number('Height (cm) *').classes('w-full bg-white text-gray-800')
#             fitness_goal = ui.select(
#                 ['Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'General Fitness'],
#                 label='Fitness Goal *'
#             ).classes('w-full bg-white').style('color: #1a1a1a !important')

#             fitness_level = ui.select(
#                 ['Beginner', 'Intermediate', 'Advanced'],
#                 label='Fitness Level *'
#             ).classes('w-full bg-white').style('color: #1a1a1a !important')
#             health_conditions = ui.textarea('Health Conditions').classes('w-full bg-white text-gray-800')

#             ui.button(
#                 'Save Details',
#                 on_click=save_details
#             ).classes('w-full bg-cyan-500 text-white rounded-full hover:bg-cyan-600 transition-colors mt-4')