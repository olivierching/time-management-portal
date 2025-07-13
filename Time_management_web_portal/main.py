from flask import Flask
from dotenv import load_dotenv
import os

# Import route registration functions
from routes.auth_routes import register_auth_routes
from routes.dashboard_routes import register_dashboard_routes
from routes.incident_routes import register_incident_routes
from routes.change_routes import register_change_routes
from routes.task_routes import register_task_routes
from routes.user_routes import register_user_routes

# Initialize Flask app
app = Flask(__name__)
load_dotenv()

# Configure app settings
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Register all route modules
register_auth_routes(app)
register_dashboard_routes(app)
register_incident_routes(app)
register_change_routes(app)
register_task_routes(app)
register_user_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
