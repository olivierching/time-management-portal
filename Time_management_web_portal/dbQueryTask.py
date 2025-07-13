from warnings import filters
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
    
def task_type(db):
    """Get all available task types."""
    query = "SELECT Name FROM Alias where Object_Type_ID=8"
    result = db.execute_query(query)
    
    if result:
        return result
    return []  # Return empty list instead of None

def get_task_sub_types(db, task_type):
    """Get task subtypes for a given task type name."""
    # First get the sequence number for this task type
    seq_query = "SELECT Sequence_No FROM Alias WHERE Object_Type_ID=8 AND Name=?"
    seq_result = db.execute_query(seq_query, (task_type,))
    
    if not seq_result:
        return []
    
    # Get the sequence number (1 for ASR, 2 for Project)
    sequence_no = seq_result[0][0]
    
    # Now get all subtypes that match this sequence number as Object_Sub_Type_ID
    query = "SELECT Name FROM Alias WHERE Object_Type_ID=9 AND Object_Sub_Type_ID=? ORDER BY Sequence_No"
    result = db.execute_query(query, (sequence_no,))
    
    return result if result else []  # Return empty list if no results

def get_task_details(db,filters=None, show_all=False):
    """
    Get task ticket details with optional filtering.
    Args:
        db: Database connection
        filters: Dictionary containing filter parameters
    """    
    query = """
            SELECT ID, Task_Type, Task_Sub_Type, Ticket_ID, Status, Task_Owner,
                   Task_Create_Date, Task_Close_date, Task_Last_Update, 
                   Time_Spent_On_Task, Description
            FROM Task_Ticket
            WHERE 1=1
            """
    
    params = []

    print(f"Filters: {filters}")

    if filters:
        if filters.get('task_owner'):
           query += " AND task_owner = ?"
           params.append(filters['task_owner'])
    
        if filters.get('task_type'):
           query += " AND Task_Type = ?"
           params.append(filters['task_type'])
                
        if filters.get('sub_type'):
           query += " AND Task_Sub_Type = ?"
           params.append(filters['sub_type'])
                
        if filters.get('date_from'):
           query += " AND datetime(Task_Create_Date) >= datetime(?)"
           params.append(filters['date_from'] + " 00:00:00")

               
        if filters.get('date_to'):
           query += " AND datetime(Task_Create_Date) <= datetime(?)"
           params.append(filters['date_to'] + " 23:59:59")

        if len(filters) > 1 and filters.get('status')!='1':
            if filters.get('status'):
               query += " AND Status = ?"
               params.append(filters['status'])
        elif len(filters)==1:
            query += " AND Status !=? "
            params.append("Closed")
        

        if filters.get('ticket_id'):
           query += " AND Ticket_ID LIKE ?"
           params.append(f"%{filters['ticket_id']}%")

    query += " ORDER BY ID, Task_Create_Date DESC"
    return db.execute_query(query, tuple(params))

def get_single_task(db, task_id):
    """
    Get details of a single task.
    Args:
        db: Database connection
        task_id: ID of the task to retrieve
    """
    query = """
            SELECT ID, Task_Type, Task_Sub_Type, Ticket_ID, Status, Task_Owner,
                   Task_Create_Date, Task_Close_date, Task_Last_Update, 
                   Time_Spent_On_Task, Description
            FROM Task_Ticket WHERE ID = ?
            """
    result = db.execute_query(query, (task_id,))
    
    if result:
        task = result[0]
        return {
            'ID': task[0],
            'Task_Type': task[1],
            'Task_Sub_Type': task[2],
            'Ticket_ID': task[3],
            'Status': task[4],
            'Task_Owner': task[5],
            'Task_Create_Date': task[6],
            'Task_Close_date': task[7],
            'Task_Last_Update': task[8],
            'Time_Spent_On_Task': task[9],
            'Description': task[10]
        }
    return None

def create_task(db, task_type, task_sub_type, ticket_id, description, task_owner=None, time_spent=0, task_create_date=None, task_close_date=None, status='Open'):
    """
    Create a new task ticket.
    Args:
        db: Database connection
        task_type: Type of the task
        task_sub_type: Sub-type of the task
        ticket_id: Associated ticket ID
        description: Task description
        task_owner: Owner of the task (optional)
        time_spent: Time spent on task (default 0)
        task_create_date: Date when the task was created (optional, defaults to current datetime)
        task_close_date: Date when the task was closed (optional)
        status: Status of the task (default 'Open')
    """
    print(f"Creating task with type: {task_type}, sub-type: {task_sub_type}, ticket_id: {ticket_id}, status: {status}")
    if task_create_date is None:
        task_create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        # Convert the ISO format to our database format
        try:
            dt = datetime.fromisoformat(task_create_date)
            task_create_date = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
            
    if task_close_date:
        try:
            dt = datetime.fromisoformat(task_close_date)
            task_close_date = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass


    query = """
            INSERT INTO Task_Ticket (
                Task_Type, Task_Sub_Type, Ticket_ID, Status, Task_Owner,
                Task_Create_Date, Task_Close_date, Time_Spent_On_Task,
                Description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
    return db.execute_query(query, (
        task_type, task_sub_type, ticket_id, status, task_owner,
        task_create_date, task_close_date, time_spent, description
    ))

def update_task(db, task_id, task_type, task_sub_type, task_create_date=None, time_spent=None, description=None,
                task_close_date=None, status=None, ticket_id=None, task_owner=None):
    """
    Update a task ticket.
    Args:
        db: Database connection
        task_id: ID of the task to update
        task_create_date: New task creation date (optional)
        time_spent: New time spent value (optional)
        description: New description (optional)
        task_close_date: Task close date (optional)
        status: Task status (optional)
        ticket_id: Associated ticket ID (optional)
        task_owner: Task owner (optional)
    """
    updates = []
    params = []  # Always include task_id as the first parameter

    print(f"Updating task {task_id} with type: {task_type}, sub-type: {task_sub_type}, create date: {task_create_date}, time spent: {time_spent}, description: {description}, close date: {task_close_date}, status: {status}, ticket ID: {ticket_id}, owner: {task_owner}")

    if task_type is not None:
        updates.append("Task_type = ?")
        params.append(task_type)
    
    if task_sub_type is not None:
        updates.append("Task_sub_type = ?")
        params.append(task_sub_type)


    if task_create_date is not None:
        updates.append("Task_Create_Date = ?")
        params.append(task_create_date)
    
    if time_spent is not None:
        updates.append("Time_Spent_On_Task = ?")
        params.append(time_spent)
    
    if description is not None:
        updates.append("Description = ?")
        params.append(description)
        
    if task_close_date is not None:
        updates.append("Task_Close_date = ?")
        params.append(task_close_date)
    
    if status is not None:
        updates.append("Status = ?")
        params.append(status)
        
    if ticket_id is not None:
        updates.append("Ticket_ID = ?")
        params.append(ticket_id)
        
    if task_owner is not None:
        updates.append("Task_Owner = ?")
        params.append(task_owner)
        
    if not updates:
        return None
    
    print(f"Updates to apply: {updates}, with params: {params}")
    
    # Always update Task_Last_Update when any change is made
    updates.append("Task_Last_Update = datetime('now')")
    params.append(task_id)
    
    query = f"""
            UPDATE Task_Ticket 
            SET {', '.join(updates)}
            WHERE ID = ?
            """
    
    print(f"Updating task with query: {query} and params: {params}")
    return db.execute_query(query, tuple(params))

def create_task_for_change(db, change_id, task_data):
    """Create a new task linked to a change ticket."""
    query = """
        INSERT INTO Task_Ticket (
            Task_Type,
            Task_Sub_Type,
            Ticket_ID,
            Status,
            Description,
            Task_Create_Date
        ) VALUES (?, ?, ?, 'Open', ?, ?)
    """
    try:
        params = (
            task_data['task_type'],
            task_data['task_sub_type'],
            change_id,
            task_data['description'],
            task_data['task_create_date']
        )
        result = db.execute_query(query, params)
        return True, "Task created successfully"
    except Exception as e:
        return False, str(e)


def delete_task(db, task_id):
    """
    Delete a task ticket.
    Args:
        db: Database connection
        task_id: ID of the task to delete
    Returns:
        Boolean indicating success
    """
    try:
        query = "DELETE FROM Task_Ticket WHERE ID = ?"
        db.execute_query(query, (task_id,))
        return True
    except Exception as e:
        raise Exception(f"Error deleting task: {str(e)}")



