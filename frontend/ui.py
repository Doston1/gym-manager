import multiprocessing
from nicegui import ui

# Import page components
from .pages.home_page import home_page
from .pages.classes import classes_page
from .pages.training import training_page

ui.add_head_html('''
<script>
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.hash.includes('id_token')) {
        const hashParams = new URLSearchParams(window.location.hash.substr(1));
        const token = hashParams.get('id_token');
        if (token) {
            localStorage.setItem('token', token);
            window.location.hash = '';  // Remove token from URL
        }
    }
});
</script>
''')

# Define UI Pages
ui.page('/')(home_page)
ui.page('/classes')(classes_page)
ui.page('/training-plans')(training_page)

# Run UI Server
if __name__ in {"__main__", "__mp_main__"}:
    if multiprocessing.current_process().name == "MainProcess":
        print("In ui.py")
    ui.run(port=8080, title="GYMO", reload=True)
