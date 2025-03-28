import multiprocessing
from nicegui import ui, app
import asyncio

# Import page components
from .pages.home_page import home_page
from .pages.classes import classes_page
from .pages.training import training_page

# ui.add_head_html('''
# <script>
# document.addEventListener('DOMContentLoaded', () => {
#     if (window.location.hash.includes('id_token')) {
#         const hashParams = new URLSearchParams(window.location.hash.substr(1));
#         const token = hashParams.get('id_token');
#         if (token) {
#             localStorage.setItem('token', token);
#             window.location.hash = '';  // Remove token from URL
#         }
#     }
# });
# </script>
# ''')

app.add_static_files('/static', 'frontend/static')


# Define UI Pages
ui.page('/')(home_page)
ui.page('/classes')(classes_page)
ui.page('/training-plans')(training_page)

@ui.page('/callback')
async def callback_page():
    ui.label("Logging you in...")
    
    # Wait a short moment to make sure the browser is ready
    await asyncio.sleep(2)

    # Use JS to store token and clean URL
    await ui.run_javascript('''
        const hashParams = new URLSearchParams(window.location.hash.substr(1));
        const token = hashParams.get('id_token');
        if (token) {
            localStorage.setItem('token', token);
            window.location.hash = '';
        }
    ''')

    await asyncio.sleep(0.3)

    # Navigate to home
    ui.navigate.to('/')


# Run UI Server
if __name__ in {"__main__", "__mp_main__"}:
    if multiprocessing.current_process().name == "MainProcess":
        print("In ui.py")
    ui.run(port=8080, title="GYMO", reload=True)
