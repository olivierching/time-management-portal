from dotenv import load_dotenv
from requests import session
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

def get_change_details(db, username, filters=None, show_all=False):
    """
    Get change ticket details with optional filtering.
    Args:
        db: Database connection
        username: Username to filter by (matches Change_Delegation)
        filters: Dictionary containing filter parameters
        show_all: If True, shows all changes including completed ones
    """    
    query = """
        SELECT ID, Change_Ticket_ID, Impact_Service, Task_name, Change_state,
               Request_Ticket_ID, Task_Start_Date, Task_End_Date, Time_Spent, Assignment_Group,
               Request_By, Change_Delegation
        FROM Change_Ticket
        WHERE 1 = 1 
    """
    # params = [username]
    params=[]    
    # By default, only show active changes unless show_all is True
    if not show_all:
        query += " AND Change_state NOT IN ('Completed', 'Cancelled')"

    if filters:
        if filters.get('ticket_id'):
            query += " AND Change_Ticket_ID LIKE ?"
            params.append(f"%{filters['ticket_id']}%")

        if filters.get('change_state') and filters['change_state'] != 'All':
            query += " AND Change_state = ?"
            params.append(filters['change_state'])

        if filters.get('date_from'):
            query += " AND Task_Start_Date >= ?"
            params.append(filters['date_from'])
        
        if filters.get('date_to'):
            query += " AND Task_Start_Date <= ?"
            params.append(filters['date_to'])

    return db.execute_query(query, tuple(params))


def get_single_change(db, ticket_id):
    """
    Get details of a single change ticket.
    Args:
        db: Database connection
        ticket_id: ID of the change ticket to retrieve
    """
    query = """
            SELECT ID, Change_Ticket_ID, Impact_Service, Task_name, Change_state,
                   Request_Ticket_ID, Task_Start_Date, Task_End_Date, Time_Spent, Assignment_Group,
                   Request_By, Change_Delegation
            FROM Change_Ticket WHERE ID = ?
            """
    result = db.execute_query(query, (ticket_id,))
    if result:
        change = result[0]
        return {
            'ID': change[0],
            'Change_Ticket_ID': change[1],
            'Impact_Service': change[2],
            'Task_name': change[3],
            'Change_state': change[4],
            'Request_Ticket_ID': change[5],
            'Task_Start_Date': change[6],
            'Task_End_Date': change[7],
            'Time_Spent': change[8],
            'Assignment_Group': change[9],
            'Request_By': change[10],
            'Change_Delegation': change[11]
        }
    return None

def update_change(db, ticket_id, **kwargs):
    """
    Update a change ticket.
    Args:
        db: Database connection
        ticket_id: ID of the change ticket to update
        **kwargs: Fields to update and their new values
    """
    # Build dynamic query based on provided arguments
    columns = []
    values = []

    valid_fields = {
        'Change_Ticket_ID', 'Impact_Service', 'Task_name', 'Change_state',
        'Request_Ticket_ID', 'Task_Start_Date', 'Task_End_Date', 'Time_Spent',
        'Assignment_Group', 'Request_By', 'Change_Delegation'
    }

    for field, value in kwargs.items():
        if field in valid_fields and value is not None:
            columns.append(f"{field} = ?")
            values.append(value)

    if not columns:
        raise ValueError("No valid fields to update.")

    query = f"""
        UPDATE Change_Ticket
        SET {', '.join(columns)}
        WHERE ID = ?
    """
    values.append(ticket_id)
    return db.execute_query(query, tuple(values))

def create_task_from_change(db, username, change_ticket_id):
    """
    Create a new task from a change ticket.
    Args:
        db: Database connection
        change_ticket_id: ID of the change ticket to create task from
    Returns:
        Tuple (success: bool, message: str)
    """
    try:        
        # First get the change ticket details
        query = """
            SELECT Change_Ticket_ID, Task_name, Impact_Service, Change_Delegation
            FROM Change_Ticket 
            WHERE Change_Ticket_ID = ?
        """
        change = db.execute_query(query, (change_ticket_id,))
        
        if not change:
            return False, "Change ticket not found"
            
        change = change[0]  # Get first row
        
        # Insert the new task
        insert_query = """
            INSERT INTO Task_Ticket (
                Task_Type,
                Task_Sub_Type,
                Description,
                Ticket_ID,
                Status,
                Task_Owner,
                Task_Create_Date,
                Time_Spent_On_Task
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        print(f"Inserting task  with params: {insert_query}")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Inserting task  with params: {insert_query}")

        params = (
            'ASR',  # Task_Type
            'Change ticket follow up',  # Task_Sub_Type
            f'{change[1]}',  # Description (using Task_name from change)
            change[0],  # Ticket_ID (Change_Ticket_ID)
            'Open',  # Status
            username,  # Task_Owner (Change_Delegation)
            current_time,  # Task_Create_Date
            0  # Time_Spent_On_Task
        )
        print(f"Inserting task {insert_query} with params: {params}")
        db.execute_query(insert_query, params)
        return True, "Task created successfully"
        
    except Exception as e:
        return False, f"Error creating task: {str(e)}"

# Example usage and testing (commented out)
DATABASE_URL = get_env_variable("DATABASE_URL")
# db = dbconn.DBConnecter(DATABASE_URL)
# db.open()
# changes = get_change_details(db, "Kun")
# print(changes)
# db.close()
