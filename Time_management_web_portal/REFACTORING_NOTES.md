# Project Structure Refactoring

This document explains the new modular structure of the Time Management Web Portal.

## Overview

The original `main.py` file contained all route handlers in a single file, making it difficult to maintain and navigate. The code has been refactored into separate modules for better organization.

## New Structure

```
├── main.py                 # Main Flask application entry point
├── routes/                 # Route modules directory
│   ├── __init__.py        # Routes module initialization
│   ├── auth_routes.py     # Authentication routes (login, logout)
│   ├── dashboard_routes.py # Dashboard and main page routes
│   ├── incident_routes.py # Incident management routes
│   ├── change_routes.py   # Change management routes
│   ├── task_routes.py     # Task management routes
│   └── user_routes.py     # User management routes (password change)
├── dbQuery*.py            # Database query modules (unchanged)
├── templates/             # HTML templates (unchanged)
└── static/               # Static files (unchanged)
```

## Route Modules

### auth_routes.py
- `GET,POST /login` - User authentication
- `GET /logout` - User logout
- `GET /` - Index page (redirects to dashboard or login)

### dashboard_routes.py
- `GET /dashboard` - Main dashboard with task statistics and charts

### incident_routes.py
- `GET /incidents` - List and filter incidents
- `GET /get_incident/<ticket_id>` - Get single incident details
- `POST /update_incident` - Update incident information
- `POST /create_task_for_incident` - Create task from incident

### change_routes.py
- `GET /changes` - List and filter changes
- `GET /get_change/<ticket_id>` - Get single change details
- `POST /update_change` - Update change information
- `POST /create_task_for_change` - Create task from change

### task_routes.py
- `GET /tasks` - List and filter tasks
- `GET /get_task/<ticket_id>` - Get single task details
- `GET /get_task_sub_types/<task_type>` - Get task subtypes
- `POST /update_task` - Update task information
- `POST /create_task` - Create new task
- `POST /delete_task/<task_id>` - Delete task (with confirmation)

### user_routes.py
- `GET,POST /change-password` - Change user password
- `GET /user-management` - User management page (admin only)
- `GET /get_all_users` - Get all users (admin only)
- `POST /search_users` - Search/filter users (admin only)
- `POST /add_user` - Add new user (admin only)
- `POST /update_user` - Update user information (admin only)
- `POST /delete_user/<user_id>` - Delete user (admin only)

## Benefits of Refactoring

1. **Better Organization**: Related routes are grouped together in logical modules
2. **Easier Maintenance**: Each module can be modified independently
3. **Improved Readability**: Smaller files are easier to navigate and understand
4. **Better Testing**: Individual modules can be tested in isolation
5. **Team Development**: Multiple developers can work on different modules simultaneously
6. **Reduced Merge Conflicts**: Changes in one module won't affect others

## How It Works

1. `main.py` imports all route registration functions from the route modules
2. Each route module contains a registration function that adds routes to the Flask app
3. All modules share the same database configuration through environment variables
4. Session management and authentication checks remain consistent across all modules

## Usage

The application works exactly the same as before from a user perspective. All URLs and functionality remain unchanged. The refactoring is purely internal code organization.

To run the application:
```bash
python main.py
```

## Adding New Routes

To add new routes:

1. Create a new route module in the `routes/` directory if needed
2. Define your routes within a registration function
3. Import and call the registration function in `main.py`

Example:
```python
# routes/new_module.py
def register_new_routes(app):
    @app.route('/new-route')
    def new_route():
        return "Hello from new route!"

# main.py
from routes.new_module import register_new_routes
register_new_routes(app)
```
