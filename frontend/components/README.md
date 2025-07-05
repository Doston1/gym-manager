# Navbar Component

This centralized navbar component eliminates code duplication across pages and provides consistent navigation throughout the application.

## Features

- **Consistent styling**: Applied across all pages
- **User authentication**: Automatic user detection and menu display
- **Conditional buttons**: Support for showing/hiding buttons based on conditions
- **Reusable functions**: Shared `get_current_user()` and `logout()` functions

## Usage

### Basic Navbar

```python
from frontend.components.navbar import create_navbar, apply_page_style

async def my_page():
    # Apply consistent page styling
    apply_page_style()

    # Create navbar and get user
    user = await create_navbar()

    # Rest of your page content...
```

### Navbar with Additional Buttons

```python
from frontend.components.navbar import create_navbar, apply_page_style

async def my_page():
    apply_page_style()

    # Define additional buttons
    additional_buttons = [
        {
            'label': 'Weekly Schedule',
            'on_click': lambda: ui.navigate.to('/weekly-schedule'),
            'classes': 'text-white hover:text-blue-300'
        }
    ]

    user = await create_navbar(additional_buttons=additional_buttons)
```

### Navbar with Conditional Buttons

```python
from frontend.components.navbar import create_navbar_with_conditional_buttons, apply_page_style

async def my_page():
    apply_page_style()

    # Define conditional buttons
    conditional_buttons = [
        {
            'condition_func': my_condition_function,
            'label': 'Special Feature',
            'on_click': lambda: ui.navigate.to('/special-feature'),
            'classes': 'text-white hover:text-blue-300'
        }
    ]

    user = await create_navbar_with_conditional_buttons(check_functions=conditional_buttons)
```

## Functions

### `create_navbar(additional_buttons=None, show_user_menu=True)`

Creates a standard navbar with optional additional buttons.

**Parameters:**

- `additional_buttons`: List of button configurations
- `show_user_menu`: Whether to show user dropdown menu

**Returns:** User object if logged in, None otherwise

### `create_navbar_with_conditional_buttons(check_functions=None, show_user_menu=True)`

Creates a navbar with conditional buttons that appear based on runtime conditions.

**Parameters:**

- `check_functions`: List of conditional button configurations
- `show_user_menu`: Whether to show user dropdown menu

**Returns:** User object if logged in, None otherwise

### `apply_page_style()`

Applies consistent page styling (background gradient, colors, fonts).

### `get_current_user()`

Retrieves the current user from localStorage token.

**Returns:** User object if logged in, None otherwise

### `logout()`

Logs out the user and clears authentication tokens.

## Button Configuration

### Standard Button

```python
{
    'label': 'Button Text',
    'on_click': callback_function,
    'classes': 'optional-css-classes'
}
```

### Conditional Button

```python
{
    'condition_func': async_condition_function,
    'label': 'Button Text',
    'on_click': callback_function,
    'classes': 'optional-css-classes'
}
```

## Migration from Old Navbar

### Before (duplicated code)

```python
async def my_page():
    ui.query('body').style('background: linear-gradient(to bottom, #001f3f, #001a33); color: white; font-family: "Orbitron", sans-serif;')

    with ui.header().classes('bg-transparent text-white p-4 flex justify-between items-center shadow-lg backdrop-blur-md'):
        ui.label('Gym Manager').classes('text-2xl font-bold cursor-pointer hover:scale-105 transition-transform').on('click', lambda: ui.navigate.to('/'))
        # ... 20+ lines of navbar code ...

    user = await get_current_user()
```

### After (using component)

```python
async def my_page():
    apply_page_style()
    user = await create_navbar()
```

## Updated Files

The following files have been updated to use the new navbar component:

- `frontend/pages/my_training_plans.py`
- `frontend/pages/my_bookings.py`
- `frontend/pages/profile.py`
- `frontend/pages/home_page.py`
- `frontend/pages/classes.py`
- `frontend/pages/training.py`
- `frontend/pages/training_preferences.py`

## Benefits

1. **Code Reduction**: Eliminates ~20 lines of duplicate code per page
2. **Consistency**: Ensures all pages have identical navbar styling and behavior
3. **Maintainability**: Changes to navbar only need to be made in one place
4. **Flexibility**: Easy to add conditional buttons or page-specific buttons
5. **User Experience**: Consistent navigation across the entire application
