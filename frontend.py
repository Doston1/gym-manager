from nicegui import ui
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
import backend  # Import FastAPI backend

def get_user(request: Request):
    return request.session.get("user")

@ui.page("/")
def home(request: Request):
    user = get_user(request)

    if not user:
        return RedirectResponse(url="/login")

    with ui.row().classes("justify-between w-full p-4"):
        ui.label(f"Welcome, {user['name']}!").classes("text-xl font-bold")
        ui.button("Logout", on_click=lambda: ui.open("/logout")).classes("bg-red-500 text-white")

    ui.label("This is the gym management system dashboard.")
    ui.button("View Classes", on_click=lambda: ui.notify("Coming soon!")).classes("mt-4")

ui.run(title="Gym Management App", port=8000)
