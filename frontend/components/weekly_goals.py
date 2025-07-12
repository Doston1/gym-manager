import httpx
from nicegui import ui
from ..config import API_HOST, API_PORT

async def render_weekly_goals_section(member_id, week_start_date, token, readonly=False):
    """
    Render weekly training goals section
    
    Args:
        member_id: The member's ID
        week_start_date: The start date of the week in ISO format (YYYY-MM-DD)
        token: Authentication token
        readonly: Whether the form should be read-only
    """
    # Fetch existing goal
    headers = {"Authorization": f"Bearer {token}"}
    existing_goal = {}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'http://{API_HOST}:{API_PORT}/training/members/{member_id}/weekly-goals/{week_start_date}',
                headers=headers
            )
            if response.status_code == 200:
                existing_goal = response.json()
            elif response.status_code != 404:  # 404 is normal for no goal set yet
                ui.notify(f'Error fetching weekly goals: {response.text}', color='negative')
                print(f"Error response: {response.status_code} - {response.text}")
    except Exception as e:
        ui.notify(f'Connection error: {str(e)}', color='negative')
        print(f"Exception: {str(e)}")
    
    with ui.card().classes('w-full p-6 mb-6 bg-green-50 dark:bg-green-900 rounded-lg shadow-md'):
        ui.label('Weekly Training Goals').classes('text-2xl font-semibold mb-4 text-green-700 dark:text-green-300')
        
        ui.label('Set how many training sessions you want to have in the upcoming week').classes(
            'mb-4 text-gray-600 dark:text-gray-300'
        )
        
        with ui.grid(columns=3).classes('gap-4 w-full'):
            min_sessions = ui.input('Minimum Sessions', 
                                  value=existing_goal.get('min_sessions', 1)
                                 ).props('outlined min=1 max=7').classes('bg-white dark:bg-gray-800 rounded-md')
            
            desired_sessions = ui.input('Target Sessions', 
                                      value=existing_goal.get('desired_sessions', 3)
                                     ).props('outlined min=1 max=7').classes('bg-white dark:bg-gray-800 rounded-md')
            
            max_sessions = ui.input('Maximum Sessions', 
                                  value=existing_goal.get('max_sessions', 5)
                                 ).props('outlined min=1 max=7').classes('bg-white dark:bg-gray-800 rounded-md')
            
            # Simple validation on the frontend
            min_sessions.bind_value_to(desired_sessions, 'min', lambda x: max(1, min(int(x) if x else 1, int(desired_sessions.value) if desired_sessions.value else 1)))
            max_sessions.bind_value_to(desired_sessions, 'max', lambda x: min(7, max(int(x) if x else 7, int(desired_sessions.value) if desired_sessions.value else 7)))
        
        with ui.row().classes('w-full mt-4 items-center'):
            ui.label('Priority Level:').classes('text-gray-700 dark:text-gray-300')
            priority_options = ['Low', 'Medium', 'High']
            priority_level = ui.select(
                options=priority_options,
                value=existing_goal.get('priority_level', 'Medium')
            ).classes('ml-4 bg-white dark:bg-gray-800 rounded-md')
        
        notes = ui.textarea('Additional Notes', 
                          value=existing_goal.get('notes', '')
                         ).props('outlined').classes('bg-white dark:bg-gray-800 w-full mt-4 rounded-md')
        
        if not readonly:
            # Save button
            with ui.row().classes('justify-end mt-4'):
                ui.button('Save Weekly Goals', 
                         on_click=lambda: save_weekly_goals(
                             member_id, 
                             week_start_date, 
                             token,
                             {
                                 'member_id': member_id,
                                 'week_start_date': week_start_date,
                                 'desired_sessions': int(desired_sessions.value),
                                 'priority_level': priority_level.value,
                                 'notes': notes.value
                             }
                         )
                        ).props('color=green').classes('text-white font-bold py-2 px-4 rounded')
        
        # Add an info section about the feature
        with ui.expansion('Why set weekly goals?').classes('mt-4 bg-green-100 dark:bg-green-800 p-2 rounded-md'):
            ui.label(
                'Setting weekly goals helps our scheduling system optimize your training experience. '
                'By knowing how many sessions you prefer in a week, we can better distribute classes '
                'and ensure you get the training frequency that matches your fitness objectives.'
            ).classes('text-sm text-gray-600 dark:text-gray-300 p-2')

async def save_weekly_goals(member_id, week_start_date, token, goal_data):
    """Save weekly training goals"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'http://{API_HOST}:{API_PORT}/training/weekly-goals/upsert',
                headers=headers,
                json=goal_data
            )
            
            if response.status_code in (200, 201):
                ui.notify('Weekly goals saved successfully', color='positive')
            else:
                ui.notify(f'Error saving weekly goals: {response.text}', color='negative')
                print(f"Error response: {response.status_code} - {response.text}")
    except Exception as e:
        ui.notify(f'Connection error: {str(e)}', color='negative')
        print(f"Exception: {str(e)}")
