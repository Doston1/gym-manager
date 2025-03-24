import multiprocessing
from nicegui import ui, app
from starlette.middleware.sessions import SessionMiddleware



app.add_middleware(
    SessionMiddleware,
    secret_key='your_secret_key',  # use a secure, random key in production
    max_age=3600,                  # optional, sets cookie lifetime in seconds
    # other SessionMiddleware settings...
)
# Import page components
from .pages.home_page import home_page
from .pages.classes import classes_page
from .pages.training import training_page
# Define UI Pages
ui.page('/')(home_page)
ui.page('/classes')(classes_page)
ui.page('/training-plans')(training_page)

# Run UI Server
if __name__ in {"__main__", "__mp_main__"}:
    if multiprocessing.current_process().name == "MainProcess":
        print("In ui.py")
    ui.run(port=8080, title="GYMO", reload=True)
