from nicegui import ui
import requests
import httpx
from datetime import datetime, date, time
from frontend.config import API_HOST, API_PORT  # Import environment variables
from frontend.components.navbar import create_navbar, apply_page_style, get_current_user

async def user_full_details(user):
    # Fetch full user details from the backend
    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["auth_id"]}')
        print(f"DEBUG: user_full_details response: {response.text}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching user details: {response.status_code} - {response.text}")
            return None

async def classes_page():
    # Apply consistent page styling
    apply_page_style()

    # Create navbar and get user
    user = await create_navbar()
    
    print("In classes_page function")
    if user:
        # Fetch full user details from the backend
        print("DEBUG: classes_page.py User:", user)
        user = await user_full_details(user)
    print("DEBUG: classes_page.py User:", user)
    is_manager = user and user.get("user_type") == "manager"

    # Check if user is logged in
    if not user:
        # Show promotional message for non-logged-in users
        with ui.column().classes('w-full max-w-6xl mx-auto px-4 py-6'):
            # Header section
            ui.label('Fitness Classes at FitZone Elite').classes('text-4xl font-bold text-center mb-8 text-blue-300')
            
            # Main promotional content
            with ui.card().classes('w-full p-8 bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl shadow-2xl border border-gray-700'):
                # Hero section
                with ui.column().classes('w-full text-center mb-8'):
                    ui.icon('fitness_center').classes('text-blue-300 text-8xl mb-4')
                    ui.label('Transform Your Fitness Journey').classes('text-3xl font-bold text-blue-300 mb-4')
                    ui.label('Join our diverse range of fitness classes designed for all levels and interests.').classes('text-lg text-gray-300 mb-6 max-w-3xl mx-auto')
                
                # Class categories showcase
                with ui.row().classes('w-full justify-center gap-6 mb-8'):
                    # Strength Training
                    with ui.card().classes('p-6 bg-gradient-to-br from-red-900 to-red-800 rounded-lg border border-red-600 flex-1 max-w-xs'):
                        ui.icon('fitness_center').classes('text-red-300 text-4xl mb-3 text-center w-full')
                        ui.label('Strength Training').classes('text-xl font-bold text-red-200 mb-2 text-center')
                        ui.label('Build muscle and increase strength with our weight training and resistance classes.').classes('text-red-100 text-sm text-center')
                    
                    # Cardio & HIIT
                    with ui.card().classes('p-6 bg-gradient-to-br from-orange-900 to-orange-800 rounded-lg border border-orange-600 flex-1 max-w-xs'):
                        ui.icon('directions_run').classes('text-orange-300 text-4xl mb-3 text-center w-full')
                        ui.label('Cardio & HIIT').classes('text-xl font-bold text-orange-200 mb-2 text-center')
                        ui.label('High-intensity workouts to boost your cardiovascular health and burn calories.').classes('text-orange-100 text-sm text-center')
                    
                    # Yoga & Flexibility
                    with ui.card().classes('p-6 bg-gradient-to-br from-green-900 to-green-800 rounded-lg border border-green-600 flex-1 max-w-xs'):
                        ui.icon('self_improvement').classes('text-green-300 text-4xl mb-3 text-center w-full')
                        ui.label('Yoga & Flexibility').classes('text-xl font-bold text-green-200 mb-2 text-center')
                        ui.label('Improve flexibility, balance, and mindfulness through various yoga styles.').classes('text-green-100 text-sm text-center')
                
                # Features and benefits
                with ui.column().classes('w-full mb-8'):
                    ui.label('Why Choose Our Classes?').classes('text-2xl font-bold text-center text-blue-300 mb-6')
                    
                    with ui.grid(columns=2).classes('w-full gap-6'):
                        # Professional Trainers
                        with ui.row().classes('items-center space-x-4'):
                            ui.icon('verified').classes('text-blue-400 text-3xl')
                            with ui.column():
                                ui.label('Expert Trainers').classes('text-lg font-bold text-blue-300')
                                ui.label('Certified professionals with years of experience to guide your fitness journey.').classes('text-gray-300 text-sm')
                        
                        # Small Groups
                        with ui.row().classes('items-center space-x-4'):
                            ui.icon('groups').classes('text-green-400 text-3xl')
                            with ui.column():
                                ui.label('Small Group Sessions').classes('text-lg font-bold text-green-300')
                                ui.label('Personalized attention in intimate class settings for better results.').classes('text-gray-300 text-sm')
                        
                        # Modern Equipment
                        with ui.row().classes('items-center space-x-4'):
                            ui.icon('build').classes('text-purple-400 text-3xl')
                            with ui.column():
                                ui.label('Modern Equipment').classes('text-lg font-bold text-purple-300')
                                ui.label('State-of-the-art facilities and equipment for the best workout experience.').classes('text-gray-300 text-sm')
                        
                        # Flexible Scheduling
                        with ui.row().classes('items-center space-x-4'):
                            ui.icon('schedule').classes('text-yellow-400 text-3xl')
                            with ui.column():
                                ui.label('Flexible Scheduling').classes('text-lg font-bold text-yellow-300')
                                ui.label('Multiple time slots throughout the day to fit your busy schedule.').classes('text-gray-300 text-sm')
                
                # Call to action section
                with ui.column().classes('w-full text-center'):
                    ui.label('Ready to Start Your Fitness Journey?').classes('text-2xl font-bold text-blue-300 mb-4')
                    ui.label('Log in or sign up to view our current class schedule and reserve your spot!').classes('text-lg text-gray-300 mb-6')
                    
                    with ui.row().classes('justify-center gap-4'):
                        ui.button('Login', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes(
                            'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 '
                            'text-white px-8 py-3 rounded-lg font-semibold text-lg shadow-lg '
                            'transform hover:scale-105 transition-all duration-200'
                        )
                        ui.button('Sign Up', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes(
                            'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 '
                            'text-white px-8 py-3 rounded-lg font-semibold text-lg shadow-lg '
                            'transform hover:scale-105 transition-all duration-200'
                        )
        return

    # Main content - Full width container (for logged-in users)
    with ui.column().classes('w-full max-w-7xl mx-auto px-4 py-6'):
        # Header section
        with ui.row().classes('w-full justify-between items-center mb-8'):
            ui.label('Available Classes').classes('text-4xl font-bold text-blue-300')
            if is_manager:
                ui.button('+ Add New Class', on_click=show_add_class_form).classes(
                    'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 '
                    'text-white px-6 py-3 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200 '
                    'font-semibold text-sm'
                )
        
        # Fetch classes data
        response = requests.get("http://127.0.0.1:8000/classes")
        classes = response.json() if response.status_code == 200 else []

        # Add this debug statement
        if classes and len(classes) > 0:
            print("Class structure:", classes[0])

        if classes:
            # Filter out past classes - only show future classes
            def is_future_class(class_item):
                try:
                    class_date_str = class_item.get('date')
                    start_time = class_item.get('start_time')
                    
                    if not class_date_str:
                        return False  # Skip classes without date
                    
                    # Parse the class date
                    class_date = datetime.strptime(class_date_str, '%Y-%m-%d').date()
                    current_date = date.today()
                    
                    # If class is on a future date, it's definitely future
                    if class_date > current_date:
                        return True
                    
                    # If class is on today, check the time
                    if class_date == current_date:
                        if isinstance(start_time, (int, float)):
                            # Convert seconds to time
                            start_hours = int(start_time // 3600)
                            start_minutes = int((start_time % 3600) // 60)
                            class_time = time(start_hours, start_minutes)
                        elif isinstance(start_time, str):
                            # Parse HH:MM format
                            try:
                                start_hours, start_minutes = map(int, start_time.split(':'))
                                class_time = time(start_hours, start_minutes)
                            except:
                                return False  # Skip if time format is invalid
                        else:
                            return False  # Skip if time format is unknown
                        
                        # Compare with current time
                        current_time = datetime.now().time()
                        return class_time > current_time
                    
                    # Class is in the past
                    return False
                    
                except Exception as e:
                    print(f"Error checking if class is future: {e}")
                    return False  # Skip classes with date/time parsing errors
            
            # Filter classes to only include future ones
            future_classes = [cls for cls in classes if is_future_class(cls)]
            
            # Sort classes: available classes first (by date/time), then full classes
            def sort_classes(class_item):
                current_participants = class_item.get('current_participants', 0)
                max_participants = class_item.get('max_participants', 1)
                is_full = current_participants >= max_participants
                
                # Convert date and time for sorting
                date_str = class_item.get('date', '9999-12-31')  # Default to far future if no date
                start_time = class_item.get('start_time', 86400)  # Default to end of day if no time
                
                # Convert start_time to seconds if it's not already
                if isinstance(start_time, str):
                    try:
                        # Parse HH:MM format
                        hours, minutes = map(int, start_time.split(':'))
                        start_time_seconds = hours * 3600 + minutes * 60
                    except:
                        start_time_seconds = 86400  # Default to end of day
                else:
                    start_time_seconds = start_time
                
                # Return tuple: (is_full, date, time) for sorting
                # is_full=False comes first (0 < 1), then sort by date and time
                return (is_full, date_str, start_time_seconds)
            
            # Sort the filtered future classes
            future_classes.sort(key=sort_classes)
            
            # Only show classes if there are future classes available
            if future_classes:
                # Classes grid - responsive layout
                with ui.grid(columns='repeat(auto-fill, minmax(350px, 1fr))').classes('w-full gap-6'):
                    for gym_class in future_classes:
                        with ui.card().classes(
                            'p-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 '
                            'rounded-xl shadow-2xl hover:shadow-blue-500/20 transform hover:scale-105 '
                            'transition-all duration-300 cursor-pointer'
                        ):
                            # Class header
                            with ui.row().classes('w-full justify-between items-start mb-4'):
                                with ui.column().classes('flex-1'):
                                    class_name = gym_class.get('name', f"Class #{gym_class['class_id']}")
                                    ui.label(class_name).classes('text-xl font-bold text-blue-300 mb-1')
                                    
                                    # Status badge
                                    status = gym_class.get('status', 'Unknown')
                                    status_color = 'bg-green-500' if status == 'Scheduled' else 'bg-yellow-500'
                                    ui.label(status).classes(f'{status_color} text-white px-3 py-1 rounded-full text-xs font-medium')
                                
                                # Price tag
                                price = gym_class.get('price', 0)
                                ui.label(f'${price}').classes(
                                    'bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 '
                                    'rounded-lg font-bold text-lg shadow-lg'
                                )
                            
                            # Class details in organized sections
                            with ui.column().classes('w-full space-y-3'):
                                # Trainer and location
                                with ui.row().classes('w-full items-center space-x-4'):
                                    with ui.row().classes('items-center space-x-2'):
                                        ui.icon('person').classes('text-blue-400 text-lg')
                                        trainer_name = gym_class.get('trainer_name', f"Trainer ID: {gym_class['trainer_id']}")
                                        ui.label(trainer_name).classes('text-gray-300 font-medium')
                                    
                                    with ui.row().classes('items-center space-x-2'):
                                        ui.icon('location_on').classes('text-red-400 text-lg')
                                        hall_info = gym_class.get('hall_name', f"Hall ID: {gym_class['hall_id']}")
                                        ui.label(hall_info).classes('text-gray-300 font-medium')
                                
                                # Date and time
                                with ui.row().classes('w-full items-center space-x-4'):
                                    with ui.row().classes('items-center space-x-2'):
                                        ui.icon('calendar_today').classes('text-green-400 text-lg')
                                        date_str = gym_class.get('date', 'TBD')
                                        ui.label(date_str).classes('text-gray-300 font-medium')
                                    
                                    with ui.row().classes('items-center space-x-2'):
                                        ui.icon('schedule').classes('text-yellow-400 text-lg')
                                        # Format time display
                                        start_time = gym_class.get('start_time')
                                        end_time = gym_class.get('end_time')
                                        if isinstance(start_time, (int, float)):
                                            start_hours = int(start_time // 3600)
                                            start_minutes = int((start_time % 3600) // 60)
                                            start_time_str = f"{start_hours:02d}:{start_minutes:02d}"
                                            
                                            end_hours = int(end_time // 3600)
                                            end_minutes = int((end_time % 3600) // 60)
                                            end_time_str = f"{end_hours:02d}:{end_minutes:02d}"
                                            
                                            time_display = f"{start_time_str} - {end_time_str}"
                                        else:
                                            time_display = f"{start_time} - {end_time}"
                                        ui.label(time_display).classes('text-gray-300 font-medium')
                                
                                # Participants with progress bar
                                current_participants = gym_class.get('current_participants', 0)
                                max_participants = gym_class.get('max_participants', 1)
                                participation_rate = (current_participants / max_participants) * 100 if max_participants > 0 else 0
                                
                                with ui.column().classes('w-full space-y-2'):
                                    with ui.row().classes('w-full justify-between items-center'):
                                        ui.label('Participants').classes('text-gray-400 text-sm font-medium')
                                        ui.label(f'{current_participants}/{max_participants}').classes('text-gray-300 font-bold')
                                    
                                    # Progress bar
                                    with ui.row().classes('w-full h-2 bg-gray-700 rounded-full overflow-hidden'):
                                        progress_color = 'bg-green-500' if participation_rate < 80 else 'bg-yellow-500' if participation_rate < 100 else 'bg-red-500'
                                        ui.element('div').classes(f'{progress_color} h-full transition-all duration-300').style(f'width: {participation_rate}%')
                            
                            # Action buttons
                            with ui.row().classes('w-full justify-between items-center mt-6 pt-4 border-t border-gray-700'):
                                # Registration status
                                if current_participants >= max_participants:
                                    ui.label('FULL').classes('bg-red-500 text-white px-3 py-1 rounded-full text-xs font-bold')
                                else:
                                    available_spots = max_participants - current_participants
                                    ui.label(f'{available_spots} spots left').classes('text-green-400 text-sm font-medium')
                                
                                # Register button
                                if current_participants < max_participants:
                                    ui.button('Register Now', on_click=lambda c=class_name: ui.notify(f'Registered for {c}', type='positive')).classes(
                                        'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 '
                                        'text-white px-6 py-2 rounded-lg font-semibold text-sm shadow-lg '
                                        'transform hover:scale-105 transition-all duration-200'
                                    )
                                else:
                                    ui.button('Join Waitlist', on_click=lambda c=class_name: ui.notify(f'Added to waitlist for {c}', type='info')).classes(
                                        'bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 '
                                        'text-white px-6 py-2 rounded-lg font-semibold text-sm shadow-lg '
                                        'transform hover:scale-105 transition-all duration-200'
                                    )
            else:
                # No future classes available state
                with ui.column().classes('w-full text-center py-20'):
                    ui.icon('schedule').classes('text-gray-500 text-8xl mb-4')
                    ui.label('No upcoming classes available').classes('text-2xl text-gray-500 font-medium mb-2')
                    ui.label('All current classes have already ended. Check back for new schedules!').classes('text-gray-400')
                    if is_manager:
                        ui.button('Add Future Classes', on_click=show_add_class_form).classes(
                            'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 '
                            'text-white px-8 py-3 rounded-lg font-semibold shadow-lg mt-6 '
                            'transform hover:scale-105 transition-all duration-200'
                        )
        else:
            # No classes available state
            with ui.column().classes('w-full text-center py-20'):
                ui.icon('fitness_center').classes('text-gray-500 text-8xl mb-4')
                ui.label('No classes available at the moment').classes('text-2xl text-gray-500 font-medium mb-2')
                ui.label('Check back soon for new class schedules!').classes('text-gray-400')
                if is_manager:
                    ui.button('Create First Class', on_click=show_add_class_form).classes(
                        'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 '
                        'text-white px-8 py-3 rounded-lg font-semibold shadow-lg mt-6 '
                        'transform hover:scale-105 transition-all duration-200'
                    )

def show_add_class_form():
    with ui.dialog().props('maximized') as dialog:
        with ui.card().classes('w-full h-full bg-gray-900 text-white overflow-auto p-6'):
            # Header
            with ui.row().classes('w-full justify-between items-center mb-8'):
                ui.label('Add New Class').classes('text-3xl font-bold text-blue-300')
                ui.button('✕', on_click=dialog.close).classes(
                    'bg-red-500 hover:bg-red-600 text-white rounded-full w-10 h-10 '
                    'flex items-center justify-center font-bold text-lg'
                )
            
            # Form container - centered and responsive
            with ui.column().classes('w-full max-w-4xl mx-auto'):
                with ui.grid(columns=2).classes('w-full gap-6'):
                    # Left column
                    with ui.column().classes('space-y-4'):
                        ui.label('Class Information').classes('text-xl font-semibold text-blue-300 mb-2')
                        
                        with ui.column().classes('space-y-4'):
                            class_type_id = ui.input('Class Type ID', placeholder='Enter class type ID').classes(
                                'w-full bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400'
                            )
                            trainer_id = ui.input('Trainer ID', placeholder='Enter trainer ID').classes(
                                'w-full bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400'
                            )
                            hall_id = ui.input('Hall ID', placeholder='Enter hall ID').classes(
                                'w-full bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400'
                            )
                            date = ui.input('Date', placeholder='YYYY-MM-DD').classes(
                                'w-full bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400'
                            )
                    
                    # Right column
                    with ui.column().classes('space-y-4'):
                        ui.label('Schedule & Pricing').classes('text-xl font-semibold text-blue-300 mb-2')
                        
                        with ui.column().classes('space-y-4'):
                            start_time = ui.input('Start Time', placeholder='HH:MM (e.g., 09:30)').classes(
                                'w-full bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400'
                            )
                            end_time = ui.input('End Time', placeholder='HH:MM (e.g., 10:30)').classes(
                                'w-full bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400'
                            )
                            max_participants = ui.input('Max Participants', placeholder='Enter maximum capacity').classes(
                                'w-full bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400'
                            )
                            price = ui.input('Price ($)', placeholder='Enter class price (e.g., 15.99)').classes(
                                'w-full bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400'
                            )
                
                # Optional notes section
                with ui.column().classes('w-full mt-6'):
                    ui.label('Additional Notes (Optional)').classes('text-xl font-semibold text-blue-300 mb-2')
                    notes = ui.textarea('Class Notes', placeholder='Any additional information about this class...').classes(
                        'w-full bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 h-32'
                    )
                
                # Action buttons
                with ui.row().classes('w-full justify-center gap-4 mt-8'):
                    async def save_class():
                        try:
                            # Validate required fields
                            if not all([class_type_id.value, trainer_id.value, hall_id.value, 
                                       date.value, start_time.value, end_time.value, 
                                       max_participants.value, price.value]):
                                ui.notify('Please fill in all required fields', type='warning')
                                return
                            
                            data = {
                                "class_type_id": int(class_type_id.value),
                                "trainer_id": int(trainer_id.value),
                                "hall_id": int(hall_id.value),
                                "date": date.value,
                                "start_time": start_time.value,
                                "end_time": end_time.value,
                                "max_participants": int(max_participants.value),
                                "price": float(price.value),
                                "notes": notes.value if notes.value else None
                            }
                            
                            async with httpx.AsyncClient() as client:
                                response = await client.post("http://127.0.0.1:8000/classes", json=data)
                                
                                if response.status_code == 201:
                                    ui.notify('Class added successfully!', type='positive')
                                    dialog.close()
                                    # Refresh the page
                                    ui.navigate.to('/classes')
                                else:
                                    error_msg = response.text
                                    ui.notify(f'Failed to add class: {error_msg}', type='negative')
                        
                        except ValueError as e:
                            ui.notify('Please enter valid numeric values for IDs, participants, and price', type='warning')
                        except Exception as e:
                            print(f"Error saving class: {e}")
                            ui.notify('Error creating class. Please try again.', type='negative')
                    
                    ui.button('Create Class', on_click=save_class).classes(
                        'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 '
                        'text-white px-8 py-3 rounded-lg font-semibold text-lg shadow-lg '
                        'transform hover:scale-105 transition-all duration-200'
                    )
                    ui.button('Cancel', on_click=dialog.close).classes(
                        'bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 '
                        'text-white px-8 py-3 rounded-lg font-semibold text-lg shadow-lg '
                        'transform hover:scale-105 transition-all duration-200'
                    )
        
        dialog.open()
