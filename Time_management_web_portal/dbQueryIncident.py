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


def user_login_check(db, username, password):
    accounts = db.execute_query("SELECT ID, Account_Type, Full_Name FROM user_Account_View WHERE Login_Name = ? AND Password = ?", (username, password))
    if not accounts:
        return None, None, None,"User not found or incorrect password"
    elif len(accounts) > 1:
        return None, None, None,"Multiple accounts found for the same user"
    else:   
        return accounts[0][0], accounts[0][1],accounts[0][2], "User account is active"
    

def get_incident_details(db, username, filters=None, show_all=False):
    query = """
            SELECT ID, Incident_Ticket_ID, Impact_Service, Description, Status, 
                   Open_By, Open_Date, Close_Date, Time_Spent, Assign_Group, 
                   Assign_to, Root_Cause 
            FROM incident_ticket 
            Where 1=1 
            """
            # WHERE Assign_to = ?
            
    # params = [username]
    params = []
    print(f"Filters: {filters}, Show All: {show_all}")
    # By default, only show active incidents unless show_all is True or status filter is applied
    if not show_all and (not filters or 'status' not in filters):
        query += " AND Status NOT IN ('Resolved', 'Closed')"
    else:
        query += ""
    print(f"Query before filters: {query} filers {filters}")
    if filters:
        if filters.get('ticket_id'):
            query += " AND Incident_Ticket_ID LIKE ?"
            params.append(f"%{filters['ticket_id']}%")
        
        if filters.get('status'):
            if filters['status'] !="All":
                query += " AND Status = ?"
                print(f"Status filter applied: {filters['status']}")
                params.append(filters['status'])
        
        if filters.get('date_from'):
            query += " AND Open_Date >= ?"
            params.append(filters['date_from'])
        
        if filters.get('date_to'):
            query += " AND Open_Date <= ?"
            params.append(filters['date_to'])
    print(f"Query before filters: {query} filers {params}")        
    return db.execute_query(query, tuple(params))


def get_single_incident(db, ticket_id):
    query = """
            SELECT ID, Incident_Ticket_ID, Impact_Service, Description, Status, Open_By, Open_Date, Close_Date, Time_Spent, Assign_Group, Assign_to, Root_Cause 
            FROM incident_ticket WHERE ID = ?
            """
    result = db.execute_query(query, (ticket_id,))
    if result:
        incident = result[0]
        return {
            'ID': incident[0],
            'Incident_Ticket_ID': incident[1],
            'Impact_Service': incident[2],
            'Description': incident[3],
            'Status': incident[4],
            'Open_By': incident[5],
            'Open_Date': incident[6],
            'Time_Spent': incident[8],  # Assuming Time_Spent is at index 8
            'Close_Date': incident[7],
            'Assign_Group': incident[9],
            'Assign_to': incident[10],
            'Root_Cause': incident[11]
        }
    return None

def update_incident(db,ticket_id,ID=None,Incident_Ticket_ID=None,Impact_Service=None,Description=None,Status=None,Open_By=None,Open_Date=None,Close_Date=None,Time_Spent=None, Assign_Group=None,Assign_to=None,Root_Cause=None):
        # Build dynamic query based on provided arguments
        columns = []
        values = []

        if Incident_Ticket_ID is not None:
            columns.append("Incident_Ticket_ID = ?")
            values.append(Incident_Ticket_ID)
        if Impact_Service is not None:
            columns.append("Impact_Service = ?")
            values.append(Impact_Service)
        if Description is not None:
            columns.append("Description = ?")
            values.append(Description)
        if Status is not None:
            columns.append("Status = ?")
            values.append(Status)
        if Open_By is not None:
            columns.append("Open_By = ?")
            values.append(Open_By)
        if Open_Date is not None:
            columns.append("Open_Date = ?")
            values.append(Open_Date)
        if Close_Date is not None:
            columns.append("Close_Date = ?")
            values.append(Close_Date)
        if Assign_Group is not None:
            columns.append("Assign_Group = ?")
            values.append(Assign_Group)
        if Assign_to is not None:
            columns.append("Assign_to = ?")
            values.append(Assign_to)
        if Root_Cause is not None:
            columns.append("Root_Cause = ?")
            values.append(Root_Cause)
        if Time_Spent is not None:
            columns.append("Time_Spent = ?")
            values.append(Time_Spent)   

        if not columns:
            raise ValueError("No fields to update.")
        

        query = f"""
                    UPDATE incident_ticket
                    SET {', '.join(columns)}
                    WHERE Incident_Ticket_ID = ?
                """
        values.append(Incident_Ticket_ID)
        return db.execute_query(query, tuple(values))
