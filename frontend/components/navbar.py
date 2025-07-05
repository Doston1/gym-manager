from nicegui import ui
from frontend.config import API_HOST, API_PORT
import httpx


async def get_current_user():
    """Get current user from token stored in localStorage"""
    try:
        token = await ui.run_javascript(
            "localStorage.getItem('token')",
            timeout=5.0
        )
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://{API_HOST}:{API_PORT}/me", headers=headers)
                if response.status_code == 200:
                    return response.json()
    except Exception as e:
        print(f"Error fetching current user: {e}")
    return None


def logout():
    """Logout user and clear token"""
    ui.run_javascript("localStorage.removeItem('token'); location.reload();")
    ui.navigate.to(f"http://{API_HOST}:{API_PORT}/logout")


async def create_navbar(additional_buttons=None, show_user_menu=True):
    """
    Create a reusable navbar component
    
    Args:
        additional_buttons: List of dicts with button configurations
                           [{'label': 'Button Name', 'on_click': callback, 'classes': 'optional-classes'}]
        show_user_menu: Whether to show the user dropdown menu
    """
    user = await get_current_user()
    if user:
        # Fetch full user details from the backend
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["auth_id"]}')
                if response.status_code == 200:
                    user = response.json()
        except Exception as e:
            print(f"Error fetching user details: {e}")

    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
        
        with ui.row().classes('gap-4'):
            # Standard navigation buttons
            ui.button('Home', on_click=lambda: ui.navigate.to('/')).classes('text-white hover:text-blue-300')
            ui.button('About', on_click=lambda: ui.navigate.to('/about')).classes('text-white hover:text-blue-300')
            ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('text-white hover:text-blue-300')
            ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('text-white hover:text-blue-300')
            
            # Additional buttons if provided
            if additional_buttons:
                for btn in additional_buttons:
                    ui.button(
                        btn['label'], 
                        on_click=btn['on_click']
                    ).classes(btn.get('classes', 'text-white hover:text-blue-300'))
            
            # User menu or login button
            if user and show_user_menu:
                with ui.column():
                    user_name = user.get("first_name", user.get("name", "Account"))
                    user_button = ui.button(f'👤 {user_name} ▾').classes('text-white')
                    user_menu = ui.menu().props('auto-close').classes('bg-white text-black shadow-md rounded-md')

                    with user_menu:
                        ui.menu_item('My Profile', on_click=lambda: ui.navigate.to('/myprofile'))
                        ui.menu_item('My Bookings', on_click=lambda: ui.navigate.to('/mybookings'))
                        ui.menu_item('My Plans', on_click=lambda: ui.navigate.to('/mytrainingplans'))
                        ui.menu_item('Logout', on_click=logout)
                    user_button.on('click', user_menu.open)
            elif not user:
                ui.button('Login/Register', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('text-white hover:text-blue-300')
    
    return user


async def create_navbar_with_conditional_buttons(check_functions=None, show_user_menu=True):
    """
    Create navbar with conditional buttons based on user state or other conditions
    
    Args:
        check_functions: List of dicts with conditional button configurations
                        [{'condition_func': async_function, 'label': 'Button', 'on_click': callback, 'classes': 'optional'}]
        show_user_menu: Whether to show the user dropdown menu
    """
    user = await get_current_user()
    if user:
        # Fetch full user details from the backend
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["auth_id"]}')
                if response.status_code == 200:
                    user = response.json()
        except Exception as e:
            print(f"Error fetching user details: {e}")

    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
        
        with ui.row().classes('gap-4'):
            # Standard navigation buttons
            ui.button('Home', on_click=lambda: ui.navigate.to('/')).classes('text-white hover:text-blue-300')
            ui.button('About', on_click=lambda: ui.navigate.to('/about')).classes('text-white hover:text-blue-300')
            ui.button('Classes', on_click=lambda: ui.navigate.to('/classes')).classes('text-white hover:text-blue-300')
            ui.button('Training Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes('text-white hover:text-blue-300')
            
            # Conditional buttons
            if check_functions:
                for btn_config in check_functions:
                    try:
                        if await btn_config['condition_func']():
                            ui.button(
                                btn_config['label'], 
                                on_click=btn_config['on_click']
                            ).classes(btn_config.get('classes', 'text-white hover:text-blue-300'))
                    except Exception as e:
                        print(f"Error checking condition for button {btn_config['label']}: {e}")
            
            # User menu or login button
            if user and show_user_menu:
                with ui.column():
                    user_name = user.get("first_name", user.get("name", "Account"))
                    user_button = ui.button(f'👤 {user_name} ▾').classes('text-white')
                    user_menu = ui.menu().props('auto-close').classes('bg-white text-black shadow-md rounded-md')

                    with user_menu:
                        ui.menu_item('My Profile', on_click=lambda: ui.navigate.to('/myprofile'))
                        ui.menu_item('My Bookings', on_click=lambda: ui.navigate.to('/mybookings'))
                        ui.menu_item('My Plans', on_click=lambda: ui.navigate.to('/mytrainingplans'))
                        ui.menu_item('Logout', on_click=logout)
                    user_button.on('click', user_menu.open)
            elif not user:
                ui.button('Login/Register', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes('text-white hover:text-blue-300')
    
    return user


def apply_page_style():
    """Apply consistent page styling"""
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')
