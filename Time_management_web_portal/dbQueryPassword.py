from dotenv import load_dotenv
import dbconnecter as dbconn
import os
from datetime import datetime
import hashlib


load_dotenv()

def get_env_variable(var_name):
    """Get the environment variable or return an exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        raise EnvironmentError(f"Set the {var_name} environment variable")

def verify_current_password(db, username, current_password):
    """Verify if the current password matches the one in database."""
    # Check password directly as stored in database (no hashing)
    query = """
    SELECT Password 
    FROM Login_Account 
    WHERE Login_Name = ? AND Password = ?
    """
    
    result = db.execute_query(query, (username, current_password))
    print(f"Password verification result: {result}")
    return len(result) > 0

def update_user_password(db, username, new_password):
    """Update user's password in the database."""
    # Store password as-is to match login behavior
    query = """
    UPDATE Login_Account 
    SET Password = ?
    WHERE Login_Name = ?
    """
    
    try:
        db.execute_query(query, (new_password, username))
        return True, "Password updated successfully"
    except Exception as e:
        return False, f"Error updating password: {str(e)}"
