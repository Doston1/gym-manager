import threading
import uvicorn
from frontend.ui import ui
from backend.api import api

# Start API
def run_api():
    uvicorn.run(api, host="127.0.0.1", port=8000)

# Start UI
def run_ui():
    ui.run(port=8080, title="GYMO")

# if __name__ == "__main__":
#     threading.Thread(target=run_api, daemon=True).start()
#     run_ui()

#gibberish
