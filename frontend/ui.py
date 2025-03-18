from nicegui import ui

# Import page components
from frontend.pages.home import home_page
from frontend.pages.classes import classes_page
from frontend.pages.training import training_page

# Define UI Pages
ui.page('/')(home_page)
ui.page('/classes')(classes_page)
ui.page('/training-plans')(training_page)

# Run UI Server
if __name__ == "__main__":
    ui.run(port=8080, title="GYMO")
