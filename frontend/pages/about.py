from nicegui import ui, app
import requests
from frontend.config import API_HOST, API_PORT
import httpx
from datetime import datetime
from frontend.components.navbar import create_navbar, apply_page_style

async def about():
    # Apply consistent page styling
    apply_page_style()
    ui.query('.nicegui-content').classes('items-center')

    # Create navbar and get user
    user = await create_navbar()

    # Main content
    with ui.card().classes('w-full max-w-7xl mx-auto p-6 bg-opacity-80 bg-gray-900 rounded-lg shadow-lg'):
        ui.label('About Our Gym').classes('text-3xl font-bold text-center mb-8 text-blue-300')
        
        # About section - two paragraphs about the gym
        with ui.column().classes('w-full mb-8'):
            # First paragraph - Location and Description
            ui.label('Welcome to FitZone Elite, your premier fitness destination located in the heart of downtown Springfield at 123 Fitness Avenue. Our state-of-the-art facility spans over 15,000 square feet and features cutting-edge equipment, spacious training areas, and modern amenities designed to help you achieve your fitness goals. Strategically positioned in the bustling city center, we offer easy access via public transportation and ample parking for our valued members.').classes('text-lg text-gray-300 mb-6 leading-relaxed text-justify')
            
            # Second paragraph - Foundation and Mission
            ui.label('Founded in 2018 by fitness enthusiasts Sarah Johnson and Mike Rodriguez, FitZone Elite was born from a vision to create a welcoming and inclusive fitness community. After years of experience in the fitness industry, our founders recognized the need for a gym that combines professional-grade equipment with personalized training approaches. What started as a small neighborhood gym has grown into a thriving fitness hub, serving over 2,000 members with diverse fitness backgrounds and goals. Our mission remains unchanged: to provide exceptional fitness experiences that inspire, motivate, and transform lives.').classes('text-lg text-gray-300 mb-8 leading-relaxed text-justify')

        # Working Hours Section
        ui.label('Gym Working Hours').classes('text-2xl font-bold text-center mb-6 text-blue-300')
        
        # Get current day (0 = Sunday, 6 = Saturday)
        current_day = datetime.now().weekday()
        # Convert from Monday-based (0-6) to Sunday-based (0-6)
        current_day = (current_day + 1) % 7
        
        # Working hours data - Starting with Sunday
        schedule = [
            {"day": "Sunday", "hours": "08:00 - 20:00"},
            {"day": "Monday", "hours": "06:00 - 22:00"},
            {"day": "Tuesday", "hours": "06:00 - 22:00"},
            {"day": "Wednesday", "hours": "06:00 - 22:00"},
            {"day": "Thursday", "hours": "06:00 - 22:00"},
            {"day": "Friday", "hours": "06:00 - 21:00"},
            {"day": "Saturday", "hours": "08:00 - 20:00"}
        ]
        
        with ui.row().classes('w-full justify-between items-center gap-2 overflow-x-auto min-h-[200px] py-8 px-4'):
            for i, day_info in enumerate(schedule):
                is_current = i == current_day
                
                card_classes = 'p-4 rounded-lg shadow-md transition-all duration-300 transform hover:scale-105 flex-shrink-0 w-40'
                if is_current:
                    card_classes += ' bg-cyan-600'  # Only change background for current day
                else:
                    card_classes += ' bg-gray-800'
                
                with ui.card().classes(card_classes):
                    ui.label(day_info["day"]).classes(
                        f'text-center font-bold mb-2 text-lg '
                        f'{"text-white" if is_current else "text-blue-300"}'
                    )
                    ui.label(day_info["hours"]).classes(
                        f'text-center text-base '
                        f'{"text-white" if is_current else "text-gray-300"}'
                    )
                    if is_current:
                        ui.label('(Today)').classes('text-sm text-center mt-2 text-blue-200')
