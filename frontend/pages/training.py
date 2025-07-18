from nicegui import ui
import requests
import httpx
from frontend.config import API_HOST, API_PORT  # Import environment variables
from frontend.components.navbar import create_navbar, apply_page_style, get_current_user

async def user_full_details(user):
    # Fetch full user details from the backend
    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["auth_id"]}')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching user details: {response.status_code} - {response.text}")
            return None

async def training_page():
    # Apply consistent page styling
    apply_page_style()

    # Create navbar and get user
    user = await create_navbar()
    if user:
        # Fetch full user details from the backend
        user = await user_full_details(user)
    is_manager = user and user.get("user_type") == "manager"
    is_trainer = user and user.get("user_type") == "trainer"
    is_member = user and user.get("user_type") == "member"

    # Create a layout with sidebar and main content
    with ui.row().classes('w-full p-4 gap-4 flex-nowrap'):
        # Sidebar for navigation to training features
        with ui.card().classes('w-64 flex-shrink-0 bg-gray-900 rounded-lg shadow-lg'):
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
        with ui.card().classes('flex-1 min-w-0 p-6 bg-gray-900 rounded-lg shadow-lg'):
            # Header section
            with ui.row().classes('w-full justify-between items-center mb-6'):
                ui.label('Training Plans').classes('text-3xl font-bold text-blue-300')
                
                # Action buttons container
                with ui.row().classes('gap-2'):
                    if is_manager or is_trainer:
                        ui.button('+ Add Training Plan', on_click=lambda: show_training_plan_form(user, is_custom=False)).classes(
                            'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 '
                            'text-white px-4 py-2 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200 '
                            'font-semibold text-sm'
                        )
                    
                    if is_manager:
                        ui.button('+ Add Exercise', on_click=lambda: show_add_exercise_form(user)).classes(
                            'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 '
                            'text-white px-4 py-2 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200 '
                            'font-semibold text-sm'
                        )
                    
                    if is_member:
                        ui.button('+ Create Custom Plan', on_click=lambda: show_training_plan_form(user, is_custom=True)).classes(
                            'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 '
                            'text-white px-4 py-2 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200 '
                            'font-semibold text-sm'
                        )
            
            # Fetch training plans
            response = requests.get(f"http://{API_HOST}:{API_PORT}/training-plans")
            plans = response.json() if response.status_code == 200 else []

            if plans:
                # Training plans container with 2-column grid layout
                with ui.grid(columns=2).classes('w-full gap-4'):
                    for plan in plans:
                        with ui.card().classes(
                            'p-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 '
                            'rounded-xl shadow-2xl hover:shadow-blue-500/20 transform hover:scale-102 '
                            'transition-all duration-300'
                        ):
                            # Plan header
                            with ui.row().classes('w-full justify-between items-start mb-4'):
                                with ui.column().classes('flex-1'):
                                    plan_title = plan.get('title', 'Untitled Plan')
                                    ui.label(plan_title).classes('text-xl font-bold text-blue-300 mb-2')
                                    
                                    # Plan type badge
                                    is_custom_plan = plan.get('is_custom', False)
                                    plan_type = 'Custom' if is_custom_plan else 'Public'
                                    plan_type_color = 'bg-purple-500' if is_custom_plan else 'bg-green-500'
                                    ui.label(plan_type).classes(f'{plan_type_color} text-white px-3 py-1 rounded-full text-xs font-medium')
                                
                                # Difficulty badge
                                difficulty = plan.get('difficulty_level', 'Unknown')
                                difficulty_colors = {
                                    'Beginner': 'bg-green-500',
                                    'Intermediate': 'bg-yellow-500', 
                                    'Advanced': 'bg-red-500',
                                    'All Levels': 'bg-blue-500'
                                }
                                difficulty_color = difficulty_colors.get(difficulty, 'bg-gray-500')
                                ui.label(difficulty).classes(f'{difficulty_color} text-white px-4 py-2 rounded-lg font-bold text-sm shadow-lg')
                            
                            # Plan details in organized sections
                            with ui.column().classes('w-full space-y-3'):
                                # Duration and focus
                                with ui.row().classes('w-full items-center space-x-4'):
                                    with ui.row().classes('items-center space-x-2'):
                                        ui.icon('schedule').classes('text-cyan-400 text-lg')
                                        duration_text = f"{plan.get('duration_weeks', 'N/A')} weeks"
                                        ui.label(duration_text).classes('text-gray-300 font-medium')
                                    
                                    with ui.row().classes('items-center space-x-2'):
                                        ui.icon('fitness_center').classes('text-orange-400 text-lg')
                                        days_text = f"{plan.get('days_per_week', 'N/A')} days/week"
                                        ui.label(days_text).classes('text-gray-300 font-medium')
                                
                                # Primary and secondary focus
                                with ui.row().classes('w-full items-center space-x-4'):
                                    with ui.row().classes('items-center space-x-2'):
                                        ui.icon('target').classes('text-green-400 text-lg')
                                        primary_focus = plan.get('primary_focus', 'General Fitness')
                                        ui.label(f"Focus: {primary_focus}").classes('text-gray-300 font-medium')
                                    
                                    if plan.get('secondary_focus'):
                                        with ui.row().classes('items-center space-x-2'):
                                            ui.icon('add_circle').classes('text-blue-400 text-lg')
                                            secondary_focus = plan.get('secondary_focus')
                                            ui.label(f"+ {secondary_focus}").classes('text-gray-300 font-medium')
                                
                                # Target audience
                                with ui.row().classes('w-full items-center space-x-4'):
                                    if plan.get('target_gender') and plan['target_gender'] != 'Any':
                                        with ui.row().classes('items-center space-x-2'):
                                            ui.icon('person').classes('text-purple-400 text-lg')
                                            ui.label(f"Target: {plan['target_gender']}").classes('text-gray-300 font-medium')
                                    
                                    if plan.get('min_age') or plan.get('max_age'):
                                        with ui.row().classes('items-center space-x-2'):
                                            ui.icon('cake').classes('text-pink-400 text-lg')
                                            min_age = plan.get('min_age', 'No min')
                                            max_age = plan.get('max_age', 'No max')
                                            age_range = f"{min_age}-{max_age} years"
                                            ui.label(f"Age: {age_range}").classes('text-gray-300 font-medium')
                                
                                # Description (if available)
                                if plan.get('description'):
                                    description = plan['description']
                                    # Truncate long descriptions
                                    if len(description) > 100:
                                        description = description[:100] + "..."
                                    with ui.row().classes('w-full items-start space-x-2'):
                                        ui.icon('description').classes('text-yellow-400 text-lg mt-1')
                                        ui.label(description).classes('text-gray-400 text-sm flex-1')
                                
                                # Equipment (if specified)
                                if plan.get('equipment_needed'):
                                    equipment = plan['equipment_needed']
                                    if len(equipment) > 80:
                                        equipment = equipment[:80] + "..."
                                    with ui.row().classes('w-full items-start space-x-2'):
                                        ui.icon('build').classes('text-red-400 text-lg mt-1')
                                        ui.label(f"Equipment: {equipment}").classes('text-gray-400 text-sm flex-1')
                            
                            # Action buttons
                            with ui.row().classes('w-full justify-between items-center mt-6 pt-4 border-t border-gray-700'):
                                # Plan stats
                                plan_id = plan.get('plan_id')
                                with ui.row().classes('items-center space-x-4'):
                                    ui.label(f"Plan ID: {plan_id}").classes('text-gray-500 text-xs')
                                    if plan.get('created_at'):
                                        created_date = plan['created_at'][:10]  # Extract date part
                                        ui.label(f"Created: {created_date}").classes('text-gray-500 text-xs')
                                
                                # View button
                                ui.button('View Details', on_click=lambda p=plan: show_detailed_training_plan(p['plan_id'])).classes(
                                    'bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-600 hover:to-cyan-700 '
                                    'text-white px-6 py-2 rounded-lg font-semibold text-sm shadow-lg '
                                    'transform hover:scale-105 transition-all duration-200'
                                )
            else:
                # No training plans available state
                with ui.column().classes('w-full text-center py-20'):
                    ui.icon('assignment').classes('text-gray-500 text-8xl mb-4')
                    ui.label('No training plans available').classes('text-2xl text-gray-500 font-medium mb-2')
                    ui.label('Create your first training plan to get started!').classes('text-gray-400')
                    
                    # Call-to-action buttons based on user type
                    with ui.row().classes('justify-center gap-4 mt-6'):
                        if is_manager or is_trainer:
                            ui.button('Create Public Plan', on_click=lambda: show_training_plan_form(user, is_custom=False)).classes(
                                'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 '
                                'text-white px-8 py-3 rounded-lg font-semibold shadow-lg '
                                'transform hover:scale-105 transition-all duration-200'
                            )
                        if is_member:
                            ui.button('Create Custom Plan', on_click=lambda: show_training_plan_form(user, is_custom=True)).classes(
                                'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 '
                                'text-white px-8 py-3 rounded-lg font-semibold shadow-lg '
                                'transform hover:scale-105 transition-all duration-200'
                            )

def show_detailed_training_plan(plan_id):
    """Show detailed training plan with days and exercises"""
    try:
        # Fetch detailed training plan data
        response = requests.get(f"http://{API_HOST}:{API_PORT}/training-plans/{plan_id}/detailed")
        if response.status_code != 200:
            ui.notify('Failed to load training plan details.', color='red')
            return
        
        plan_data = response.json()
        
        # Create a modal dialog for the detailed view
        with ui.dialog().props('maximized') as dialog:
            with ui.card().classes('w-full h-full bg-gray-900 text-white overflow-auto'):
                # Header
                with ui.row().classes('w-full items-center justify-between mb-4 p-4 bg-gray-800'):
                    ui.label(plan_data['title']).classes('text-3xl font-bold text-blue-300')
                    ui.button('Close', on_click=dialog.close).classes('bg-red-500 hover:bg-red-600 text-white')
                
                # Plan Overview
                with ui.card().classes('mb-4 p-4 bg-gray-800'):
                    ui.label('Plan Overview').classes('text-xl font-bold text-blue-300 mb-2')
                    if plan_data.get('description'):
                        ui.label(f"Description: {plan_data['description']}").classes('text-gray-300 mb-1')
                    ui.label(f"Duration: {plan_data['duration_weeks']} weeks, {plan_data['days_per_week']} days per week").classes('text-gray-300 mb-1')
                    ui.label(f"Difficulty: {plan_data['difficulty_level']}").classes('text-gray-300 mb-1')
                    ui.label(f"Primary Focus: {plan_data['primary_focus']}").classes('text-gray-300 mb-1')
                    if plan_data.get('secondary_focus'):
                        ui.label(f"Secondary Focus: {plan_data['secondary_focus']}").classes('text-gray-300 mb-1')
                    if plan_data.get('target_gender') and plan_data['target_gender'] != 'Any':
                        ui.label(f"Target Gender: {plan_data['target_gender']}").classes('text-gray-300 mb-1')
                    if plan_data.get('min_age') or plan_data.get('max_age'):
                        age_range = f"{plan_data.get('min_age', 'No min')} - {plan_data.get('max_age', 'No max')} years"
                        ui.label(f"Age Range: {age_range}").classes('text-gray-300 mb-1')
                    if plan_data.get('equipment_needed'):
                        ui.label(f"Equipment: {plan_data['equipment_needed']}").classes('text-gray-300')
                
                # Days and Exercises
                if plan_data.get('days'):
                    for day in plan_data['days']:
                        with ui.card().classes('mb-4 p-4 bg-gray-800'):
                            # Day header
                            with ui.row().classes('items-center mb-3'):
                                ui.label(f"Day {day['day_number']}: {day.get('name', 'Unnamed Day')}").classes('text-lg font-bold text-cyan-300')
                                if day.get('duration_minutes'):
                                    ui.label(f"({day['duration_minutes']} min)").classes('text-gray-400 ml-2')
                                if day.get('calories_burn_estimate'):
                                    ui.label(f"~{day['calories_burn_estimate']} cal").classes('text-orange-300 ml-2')
                            
                            if day.get('focus'):
                                ui.label(f"Focus: {day['focus']}").classes('text-gray-300 mb-2')
                            if day.get('description'):
                                ui.label(f"Description: {day['description']}").classes('text-gray-300 mb-3')
                            
                            # Exercises
                            if day.get('exercises'):
                                ui.label('Exercises:').classes('text-md font-semibold text-blue-300 mb-2')
                                for exercise in day['exercises']:
                                    with ui.card().classes('ml-4 mb-2 p-3 bg-gray-700'):
                                        # Exercise header
                                        with ui.row().classes('items-center mb-1'):
                                            ui.label(f"{exercise['order']}. {exercise['exercise_name']}").classes('text-white font-semibold')
                                            if exercise.get('exercise_difficulty'):
                                                ui.label(f"({exercise['exercise_difficulty']})").classes('text-yellow-300 ml-2')
                                        
                                        # Exercise details
                                        exercise_details = []
                                        if exercise.get('sets'):
                                            exercise_details.append(f"{exercise['sets']} sets")
                                        if exercise.get('reps'):
                                            exercise_details.append(f"{exercise['reps']} reps")
                                        if exercise.get('duration_seconds'):
                                            exercise_details.append(f"{exercise['duration_seconds']}s duration")
                                        if exercise.get('rest_seconds'):
                                            exercise_details.append(f"{exercise['rest_seconds']}s rest")
                                        
                                        if exercise_details:
                                            ui.label(' | '.join(exercise_details)).classes('text-cyan-300 mb-1')
                                        
                                        if exercise.get('primary_muscle_group'):
                                            ui.label(f"Target: {exercise['primary_muscle_group']}").classes('text-green-300 mb-1')
                                        
                                        if exercise.get('exercise_description'):
                                            ui.label(f"Description: {exercise['exercise_description']}").classes('text-gray-300 mb-1')
                                        
                                        if exercise.get('exercise_instructions'):
                                            ui.label(f"Instructions: {exercise['exercise_instructions']}").classes('text-gray-300 mb-1')
                                        
                                        if exercise.get('exercise_equipment'):
                                            ui.label(f"Equipment: {exercise['exercise_equipment']}").classes('text-orange-300 mb-1')
                                        
                                        if exercise.get('notes'):
                                            ui.label(f"Notes: {exercise['notes']}").classes('text-yellow-300')
                            else:
                                ui.label('No exercises assigned to this day yet.').classes('text-gray-500 italic')
                else:
                    ui.label('No training days have been created for this plan yet.').classes('text-gray-500 italic')
        
        dialog.open()
        
    except Exception as e:
        print(f"Error showing detailed training plan: {e}")
        ui.notify('Error loading training plan details.', color='red')

def show_add_training_plan_form():
    # Show a form to add a new training plan, with training_plan_days, exercises (bring the existing exercises with an option to choose) ,training_day_exercises
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
            response = requests.post(f"http://{API_HOST}:{API_PORT}/training-plans", json=data)
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

def show_training_plan_form(user, is_custom=True):
    """Show comprehensive form for creating training plans (both custom for members and public for managers/trainers)"""
    import asyncio
    
    async def fetch_exercises():
        """Fetch available exercises for the form"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://{API_HOST}:{API_PORT}/training-plans/exercises")
                if response.status_code == 200:
                    return response.json()
                else:
                    return []
        except Exception as e:
            print(f"Error fetching exercises: {e}")
            return []
    
    # Determine theme colors and labels based on plan type
    theme_color = 'purple' if is_custom else 'green'
    theme_light = 'purple-300' if is_custom else 'green-300'
    theme_medium = 'purple-600' if is_custom else 'green-600'
    border_color = 'border-purple-500' if is_custom else 'border-green-500'
    plan_type_label = 'Custom' if is_custom else 'Public'
    header_text = f'Create Your {plan_type_label} Training Plan'
    
    # Create the dialog
    with ui.dialog().props('maximized') as dialog:
        # Add custom CSS for dropdown styling
        ui.add_head_html('''
            <style>
                .q-menu .q-item {
                    color: black !important;
                    background-color: white !important;
                }
                .q-menu .q-item:hover {
                    background-color: #f0f0f0 !important;
                    color: black !important;
                }
                .q-select .q-field__native {
                    color: black !important;
                }
                .q-field__label {
                    color: #666 !important;
                }
            </style>
        ''')
        
        with ui.card().classes('w-full h-full bg-gray-900 text-white overflow-auto p-6'):
            # Header
            with ui.row().classes('w-full items-center justify-between mb-6'):
                ui.label(header_text).classes(f'text-3xl font-bold text-{theme_light}')
                ui.button('Cancel', on_click=dialog.close).classes('bg-red-500 hover:bg-red-600 text-white px-4 py-2')
            
            # Plan basic info
            with ui.card().classes('mb-6 p-6 bg-white'):
                ui.label('Plan Information').classes(f'text-xl font-bold text-{theme_medium} mb-4')
                
                with ui.row().classes('w-full gap-4'):
                    title = ui.input('Plan Title').classes('flex-1').style('background-color: white; color: black;')
                    duration_weeks = ui.number('Duration (Weeks)', value=4, min=1, max=52).classes('w-32').style('background-color: white; color: black;')
                    days_per_week = ui.number('Days per Week', value=3, min=1, max=7).classes('w-32').style('background-color: white; color: black;')
                
                description = ui.textarea('Plan Description').classes('w-full mt-4').style('background-color: white; color: black;')
                
                # Difficulty level options vary for public vs custom plans
                difficulty_options = ['Beginner', 'Intermediate', 'Advanced'] if is_custom else ['Beginner', 'Intermediate', 'Advanced', 'All Levels']
                default_difficulty = 'Beginner' if is_custom else 'All Levels'
                
                with ui.row().classes('w-full gap-4 mt-4'):
                    difficulty_level = ui.select(difficulty_options, 
                                               label='Difficulty Level', value=default_difficulty).classes('flex-1').style('background-color: white; color: black;')
                    primary_focus = ui.select(['Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'Strength', 'General Fitness'], 
                                            label='Primary Focus', value='General Fitness').classes('flex-1').style('background-color: white; color: black;')
                    secondary_focus = ui.select(['Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'Strength', 'General Fitness'], 
                                              label='Secondary Focus (Optional)').classes('flex-1').style('background-color: white; color: black;')
                
                with ui.row().classes('w-full gap-4 mt-4'):
                    target_gender = ui.select(['Any', 'Male', 'Female'], label='Target Gender', value='Any').classes('flex-1').style('background-color: white; color: black;')
                    min_age = ui.number('Min Age', min=13, max=100).classes('w-32').style('background-color: white; color: black;')
                    max_age = ui.number('Max Age', min=13, max=100).classes('w-32').style('background-color: white; color: black;')
                
                equipment_needed = ui.textarea('Equipment Needed').classes('w-full mt-4').style('background-color: white; color: black;')
                
                # Health limitations field only for custom plans (members)
                health_limitations = None
                if is_custom:
                    health_limitations = ui.textarea('Health Limitations or Notes').classes('w-full mt-4').style('background-color: white; color: black;')
            
            # Training Days Section
            with ui.card().classes('mb-6 p-6 bg-white'):
                ui.label('Training Days').classes(f'text-xl font-bold text-{theme_medium} mb-4')
                
                # Container for training days
                days_container = ui.column().classes('w-full gap-4')
                training_days = []
                
                def add_training_day():
                    day_number = len(training_days) + 1
                    
                    with days_container:
                        with ui.card().classes(f'p-4 bg-white border-l-4 {border_color}') as day_card:
                            # Day header
                            with ui.row().classes('w-full items-center justify-between mb-4'):
                                ui.label(f'Day {day_number}').classes('text-lg font-bold text-cyan-600')
                                ui.button('Remove Day', 
                                         on_click=lambda dc=day_card: remove_day(dc)).classes('bg-red-500 hover:bg-red-600 text-white text-sm px-3 py-1')
                            
                            # Day details
                            with ui.row().classes('w-full gap-4 mb-4'):
                                day_name = ui.input('Day Name (e.g., "Upper Body")').classes('flex-1').style('background-color: white; color: black;')
                                day_focus = ui.input('Focus (e.g., "Chest and Back")').classes('flex-1').style('background-color: white; color: black;')
                                duration_minutes = ui.number('Duration (minutes)', value=60, min=15, max=180).classes('w-32').style('background-color: white; color: black;')
                            
                            day_description = ui.textarea('Day Description').classes('w-full mb-4').style('background-color: white; color: black;')
                            
                            # Exercises for this day
                            ui.label('Exercises').classes('text-md font-semibold text-blue-600 mb-2')
                            exercises_container = ui.column().classes('w-full gap-2 ml-4')
                            day_exercises = []
                            
                            async def add_exercise_to_day():
                                # Fetch exercises if not already done
                                exercises = await fetch_exercises()
                                exercise_options = {ex['exercise_id']: f"{ex['name']} ({ex['primary_muscle_group']})" for ex in exercises}
                                
                                with exercises_container:
                                    with ui.card().classes('p-3 bg-gray-100 border border-gray-300') as exercise_card:
                                        with ui.row().classes('w-full items-center justify-between mb-2'):
                                            ui.label(f'Exercise {len(day_exercises) + 1}').classes('text-md font-semibold text-gray-800')
                                            ui.button('Remove', 
                                                     on_click=lambda ec=exercise_card: remove_exercise(ec)).classes('bg-red-500 hover:bg-red-600 text-white text-xs px-2 py-1')
                                        
                                        # Exercise selection and details
                                        with ui.row().classes('w-full gap-2 mb-2'):
                                            exercise_select = ui.select(exercise_options, label='Exercise').classes('flex-1').style('background-color: white; color: black;')
                                            exercise_order = ui.number('Order', value=len(day_exercises) + 1, min=1).classes('w-20').style('background-color: white; color: black;')
                                        
                                        with ui.row().classes('w-full gap-2 mb-2'):
                                            sets = ui.number('Sets', value=3 if is_custom else None, min=1, max=20).classes('w-20').style('background-color: white; color: black;')
                                            reps = ui.input('Reps (e.g., "8-12")').classes('w-32').style('background-color: white; color: black;')
                                            rest_seconds = ui.number('Rest (seconds)', value=60 if is_custom else None, min=0, max=600).classes('w-32').style('background-color: white; color: black;')
                                            duration_seconds = ui.number('Duration (seconds)', min=0, max=600).classes('w-32').style('background-color: white; color: black;')
                                        
                                        exercise_notes = ui.input('Exercise Notes').classes('w-full').style('background-color: white; color: black;')
                                        
                                        # Store exercise data
                                        exercise_data = {
                                            'card': exercise_card,
                                            'exercise_select': exercise_select,
                                            'order': exercise_order,
                                            'sets': sets,
                                            'reps': reps,
                                            'rest_seconds': rest_seconds,
                                            'duration_seconds': duration_seconds,
                                            'notes': exercise_notes
                                        }
                                        day_exercises.append(exercise_data)
                            
                            def remove_exercise(exercise_card):
                                # Remove from day_exercises list
                                day_exercises[:] = [ex for ex in day_exercises if ex['card'] != exercise_card]
                                # Remove from UI
                                exercise_card.delete()
                            
                            # Add exercise button
                            ui.button('Add Exercise', 
                                     on_click=add_exercise_to_day).classes('bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 mt-2')
                            
                            # Store day data
                            day_data = {
                                'card': day_card,
                                'day_number': day_number,
                                'name': day_name,
                                'focus': day_focus,
                                'duration_minutes': duration_minutes,
                                'description': day_description,
                                'exercises': day_exercises
                            }
                            training_days.append(day_data)
                
                def remove_day(day_card):
                    # Remove from training_days list
                    training_days[:] = [day for day in training_days if day['card'] != day_card]
                    # Remove from UI
                    day_card.delete()
                    # Update day numbers
                    for i, day in enumerate(training_days):
                        day['day_number'] = i + 1
                
                # Add day button
                button_color = 'bg-green-500 hover:bg-green-600' if is_custom else 'bg-cyan-500 hover:bg-cyan-600'
                ui.button('Add Training Day', on_click=add_training_day).classes(f'{button_color} text-white px-4 py-2')
            
            # Action buttons
            with ui.row().classes('w-full justify-center gap-4 mt-6'):
                async def save_plan():
                    try:
                        # Get trainer_id for managers/trainers (only for public plans)
                        trainer_id = None
                        if not is_custom:
                            if user.get('user_type') == 'trainer':
                                trainer_id = user.get('user_id')  # For trainers, trainer_id = user_id
                            elif user.get('user_type') == 'manager':
                                # For managers, we could either not set created_by or ask which trainer to assign it to
                                # For now, let's allow managers to create plans without a specific trainer
                                trainer_id = None
                        
                        # Prepare plan data
                        plan_data = {
                            'title': title.value,
                            'description': description.value,
                            'difficulty_level': difficulty_level.value,
                            'duration_weeks': int(duration_weeks.value) if duration_weeks.value else 4,
                            'days_per_week': int(days_per_week.value) if days_per_week.value else 3,
                            'primary_focus': primary_focus.value,
                            'secondary_focus': secondary_focus.value if secondary_focus.value else None,
                            'target_gender': target_gender.value,
                            'min_age': int(min_age.value) if min_age.value else None,
                            'max_age': int(max_age.value) if max_age.value else None,
                            'equipment_needed': equipment_needed.value
                        }
                        
                        # Add plan type specific fields
                        if not is_custom:
                            plan_data['is_custom'] = False  # This is a public plan
                            plan_data['is_active'] = True
                            plan_data['created_by'] = trainer_id
                            print(f"Creating public plan with trainer_id: {trainer_id}")
                        
                        # Prepare days data
                        days_data = []
                        for day in training_days:
                            day_info = {
                                'day_number': day['day_number'],
                                'name': day['name'].value,
                                'focus': day['focus'].value,
                                'duration_minutes': int(day['duration_minutes'].value) if day['duration_minutes'].value else 60,
                                'description': day['description'].value,
                                'exercises': []
                            }
                            
                            # Prepare exercises data
                            for exercise in day['exercises']:
                                if exercise['exercise_select'].value:
                                    exercise_info = {
                                        'exercise_id': exercise['exercise_select'].value,
                                        'order': int(exercise['order'].value) if exercise['order'].value else 1,
                                        'sets': int(exercise['sets'].value) if exercise['sets'].value else None,
                                        'reps': exercise['reps'].value,
                                        'rest_seconds': int(exercise['rest_seconds'].value) if exercise['rest_seconds'].value else None,
                                        'duration_seconds': int(exercise['duration_seconds'].value) if exercise['duration_seconds'].value else None,
                                        'notes': exercise['notes'].value
                                    }
                                    day_info['exercises'].append(exercise_info)
                            
                            days_data.append(day_info)
                        
                        # Prepare full payload
                        payload = {
                            'plan': plan_data,
                            'days': days_data,
                            'user_id': user['user_id']
                        }
                        
                        # Add custom plan specific fields
                        if is_custom:
                            payload['member_id'] = user.get('member_id_pk')
                            payload['goal'] = plan_data['description']
                            payload['health_limitations'] = health_limitations.value if health_limitations else None
                        
                        # Determine endpoint based on plan type
                        endpoint = 'custom' if is_custom else 'public'
                        
                        # Send to backend
                        async with httpx.AsyncClient() as client:
                            response = await client.post(f"http://{API_HOST}:{API_PORT}/training-plans/{endpoint}", json=payload)
                            
                            if response.status_code == 201:
                                plan_type_msg = 'Custom' if is_custom else 'Public'
                                ui.notify(f'{plan_type_msg} training plan created successfully!', color='green')
                                dialog.close()
                                # Refresh the page
                                ui.navigate.to('/training-plans')
                            else:
                                error_msg = response.text
                                ui.notify(f'Failed to create {plan_type_label.lower()} plan: {error_msg}', color='red')
                    
                    except Exception as e:
                        print(f"Error saving {plan_type_label.lower()} plan: {e}")
                        ui.notify(f'Error creating {plan_type_label.lower()} plan. Please try again.', color='red')
                
                # Create button with appropriate styling and text
                create_button_text = f'Create {plan_type_label} Plan'
                create_button_class = f'bg-{theme_color}-500 hover:bg-{theme_color}-600 text-white px-6 py-3 text-lg'
                
                ui.button(create_button_text, 
                         on_click=save_plan).classes(create_button_class)
                ui.button('Cancel', 
                         on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 text-lg')
    
    dialog.open()

def show_add_exercise_form(user):
    """Show comprehensive form for managers to add new exercises to the database"""
    
    # Create the dialog
    with ui.dialog().props('maximized') as dialog:
        # Add custom CSS for form styling
        ui.add_head_html('''
            <style>
                .q-menu .q-item {
                    color: black !important;
                    background-color: white !important;
                }
                .q-menu .q-item:hover {
                    background-color: #f0f0f0 !important;
                    color: black !important;
                }
                .q-select .q-field__native {
                    color: black !important;
                }
                .q-field__label {
                    color: #666 !important;
                }
            </style>
        ''')
        
        with ui.card().classes('w-full h-full bg-gray-900 text-white overflow-auto p-6'):
            # Header
            with ui.row().classes('w-full items-center justify-between mb-6'):
                ui.label('Add New Exercise').classes('text-3xl font-bold text-blue-300')
                ui.button('Cancel', on_click=dialog.close).classes('bg-red-500 hover:bg-red-600 text-white px-4 py-2')
            
            # Exercise Information
            with ui.card().classes('mb-6 p-6 bg-white'):
                ui.label('Exercise Information').classes('text-xl font-bold text-blue-600 mb-4')
                
                # Basic Information
                with ui.row().classes('w-full gap-4'):
                    exercise_name = ui.input('Exercise Name *').classes('flex-1').style('background-color: white; color: black;')
                    difficulty_level = ui.select(['Beginner', 'Intermediate', 'Advanced'], 
                                               label='Difficulty Level', value='Beginner').classes('w-40').style('background-color: white; color: black;')
                
                # Muscle Groups
                with ui.row().classes('w-full gap-4 mt-4'):
                    primary_muscle_group = ui.select([
                        'Chest', 'Back', 'Shoulders', 'Arms', 'Legs', 'Core', 'Full Body', 'Cardio'
                    ], label='Primary Muscle Group *').classes('flex-1').style('background-color: white; color: black;')
                    
                    secondary_muscle_groups = ui.input('Secondary Muscle Groups (comma-separated)', placeholder='e.g., Triceps, Shoulders, Core').classes('flex-1').style('background-color: white; color: black;')
                
                # Equipment
                with ui.row().classes('w-full gap-4 mt-4'):
                    equipment_needed = ui.input('Equipment Needed', placeholder='e.g., Dumbbells, Barbell, Resistance Band, Bodyweight').classes('flex-1').style('background-color: white; color: black;')
                    is_active = ui.checkbox('Active Exercise', value=True).classes('mt-4')
                
                # Description and Instructions
                with ui.column().classes('w-full gap-4 mt-4'):
                    description = ui.textarea('Exercise Description', placeholder='Brief description of the exercise and its benefits...').classes('w-full').style('background-color: white; color: black; min-height: 100px;')
                    instructions = ui.textarea('Exercise Instructions', placeholder='Step-by-step instructions on how to perform the exercise correctly...').classes('w-full').style('background-color: white; color: black; min-height: 120px;')
                
                # Media URLs (Optional)
                with ui.row().classes('w-full gap-4 mt-4'):
                    image_url = ui.input('Image URL (optional)', placeholder='https://example.com/image.jpg').classes('flex-1').style('background-color: white; color: black;')
                    video_url = ui.input('Video URL (optional)', placeholder='https://youtube.com/watch?v=...').classes('flex-1').style('background-color: white; color: black;')
                
                # Helper text
                ui.label('* Required fields').classes('text-sm text-gray-500 mt-2')
            
            # Action buttons
            with ui.row().classes('w-full justify-center gap-4 mt-6'):
                async def save_exercise():
                    try:
                        # Validate required fields
                        if not exercise_name.value or not exercise_name.value.strip():
                            ui.notify('Exercise name is required', color='red')
                            return
                        
                        if not primary_muscle_group.value:
                            ui.notify('Primary muscle group is required', color='red')
                            return
                        
                        # Prepare exercise data
                        exercise_data = {
                            'name': exercise_name.value.strip(),
                            'description': description.value.strip() if description.value else None,
                            'instructions': instructions.value.strip() if instructions.value else None,
                            'difficulty_level': difficulty_level.value,
                            'primary_muscle_group': primary_muscle_group.value,
                            'secondary_muscle_groups': secondary_muscle_groups.value.strip() if secondary_muscle_groups.value else None,
                            'equipment_needed': equipment_needed.value.strip() if equipment_needed.value else None,
                            'image_url': image_url.value.strip() if image_url.value else None,
                            'video_url': video_url.value.strip() if video_url.value else None,
                            'is_active': is_active.value
                        }
                        
                        # Send to backend
                        async with httpx.AsyncClient() as client:
                            response = await client.post(f"http://{API_HOST}:{API_PORT}/training-plans/exercises", json=exercise_data)
                            
                            if response.status_code == 201:
                                ui.notify('Exercise created successfully!', color='green')
                                dialog.close()
                                # Refresh the page
                                ui.navigate.to('/training-plans')
                            else:
                                error_msg = response.text
                                if response.status_code == 409:
                                    ui.notify('An exercise with this name already exists', color='red')
                                else:
                                    ui.notify(f'Failed to create exercise: {error_msg}', color='red')
                    
                    except Exception as e:
                        print(f"Error saving exercise: {e}")
                        ui.notify('Error creating exercise. Please try again.', color='red')
                
                ui.button('Create Exercise', 
                         on_click=save_exercise).classes('bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 text-lg')
                ui.button('Cancel', 
                         on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 text-lg')
    
    dialog.open()
