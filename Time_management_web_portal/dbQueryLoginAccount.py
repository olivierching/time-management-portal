from dotenv import load_dotenv
import dbconnecter as dbconn
import os
from datetime import datetime

load_dotenv()

def get_env_variable(var_name):
    """Get the environment variable or return an exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        raise EnvironmentError(f"Set the {var_name} environment variable")

def get_user_by_id(db, user_id):
    """Get user details by ID."""
    query = """
        SELECT ID, Account_Type_ID, Login_Name, First_Name, Last_Name, 
               Full_Name, Email, Password
        FROM Login_Account 
        WHERE ID = ?
    """
    result = db.execute_query(query, (user_id,))
    return result[0] if result else None

def get_user_by_login(db, login_name):
    """Get user details by login name."""
    query = """
        SELECT ID, Account_Type_ID, Login_Name, First_Name, Last_Name, 
               Full_Name, Email, Password
        FROM Login_Account 
        WHERE Login_Name = ?
    """
    result = db.execute_query(query, (login_name,))
    return result[0] if result else None

def create_user(db, account_type_id, login_name, first_name, last_name, email, password):
    """Create a new user account."""
    # Create full name from first and last name
    full_name = f"{first_name} {last_name}"
    
    query = """
        INSERT INTO Login_Account (
            Account_Type_ID, Login_Name, First_Name, Last_Name,
            Full_Name, Email, Password
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    values = (account_type_id, login_name, first_name, last_name, 
              full_name, email, password)
    return db.execute_query(query, values)

def update_user(db, user_id, **kwargs):
    """
    Update user account details.
    Args:
        db: Database connection
        user_id: ID of the user to update
        **kwargs: Fields to update (account_type_id, login_name, first_name, 
                 last_name, email, password)
    """
    valid_fields = {
        'account_type_id': 'Account_Type_ID',
        'login_name': 'Login_Name',
        'first_name': 'First_Name',
        'last_name': 'Last_Name',
        'email': 'Email',
        'password': 'Password'
    }
    
    updates = []
    values = []
    
    # Special handling for first_name and last_name to update full_name
    if 'first_name' in kwargs or 'last_name' in kwargs:
        # Get current user data
        current_user = get_user_by_id(db, user_id)
        first_name = kwargs.get('first_name', current_user[3])
        last_name = kwargs.get('last_name', current_user[4])
        updates.append('Full_Name = ?')
        values.append(f"{first_name} {last_name}")
    
    # Handle other fields
    for key, value in kwargs.items():
        if key in valid_fields and value is not None:
            updates.append(f"{valid_fields[key]} = ?")
            values.append(value)
    
    if not updates:
        return None
    
    query = f"""
        UPDATE Login_Account 
        SET {', '.join(updates)}
        WHERE ID = ?
    """
    values.append(user_id)
    return db.execute_query(query, tuple(values))

def delete_user(db, user_id):
    """Delete a user account."""
    query = "DELETE FROM Login_Account WHERE ID = ?"
    return db.execute_query(query, (user_id,))

def verify_login(db, login_name, password):
    """
    Verify user login credentials.
    Returns tuple of (success, user_info, message)
    """
    query = """
        SELECT ID, Account_Type_ID, Login_Name, First_Name, Last_Name, 
               Full_Name, Email
        FROM Login_Account 
        WHERE Login_Name = ? AND Password = ?
    """
    result = db.execute_query(query, (login_name, password))
    
    if not result:
        return False, None, "Invalid login credentials"
    elif len(result) > 1:
        return False, None, "Multiple accounts found for the same login"
    else:
        user_info = {
            'id': result[0][0],
            'account_type_id': result[0][1],
            'login_name': result[0][2],
            'first_name': result[0][3],
            'last_name': result[0][4],
            'full_name': result[0][5],
            'email': result[0][6]
        }
        return True, user_info, "Login successful"

def get_all_users(db, account_type_id=None):
    """
    Get all users, optionally filtered by account type.
    Args:
        db: Database connection
        account_type_id: Optional filter by account type ID
    """
    if account_type_id:
        query = """
            SELECT ID, Account_Type_ID, Login_Name, First_Name, Last_Name, 
                   Full_Name, Email 
            FROM Login_Account 
            WHERE Account_Type_ID = ?
            ORDER BY Full_Name
        """
        return db.execute_query(query, (account_type_id,))
    else:
        query = """
            SELECT ID, Account_Type_ID, Login_Name, First_Name, Last_Name, 
                   Full_Name, Email 
            FROM Login_Account 
            ORDER BY Full_Name
        """
        return db.execute_query(query)


def get_users_name(db):
    """Get all users with account type 3."""
    query = """
            SELECT ID, Login_Name, Full_Name 
            FROM Login_Account
            WHERE Account_Type_ID = 3
            ORDER BY Full_Name
            """
    result = db.execute_query(query)
    if result:
        return list(result)
    return []



def change_password(db, user_id, new_password):
    """Change user's password."""
    query = "UPDATE Login_Account SET Password = ? WHERE ID = ?"
    return db.execute_query(query, (new_password, user_id))


def get_login_account_view(db, user_id):
    """Get login account view for a specific user."""
    query = """
        SELECT ID, Account_Type, Login_Name, First_Name, Last_Name, 
               Full_Name, Email
        FROM Account_View
        WHERE ID = ?
    """
    result = db.execute_query(query, (user_id,))
    if result:
        return result[0]
    return None

def get_user_login_account(db, user_id):
    """Get user account view for a specific user."""
    query = """
            SELECT ID,
                (SELECT Description
                    FROM Account_Type
                    WHERE ID = a.Account_Type_ID
                ) Account_Type,
                Login_Name,
                First_Name,
                Last_Name,
                Full_Name,
                Email,
                Password
            FROM Login_Account a
            WHERE ID = ?
            """
    result = db.execute_query(query, (user_id,))
    if result:
        return result[0]
    return None