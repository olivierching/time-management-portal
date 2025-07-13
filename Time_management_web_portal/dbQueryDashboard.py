from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

def get_env_variable(var_name):
    """Get the environment variable or return an exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        raise EnvironmentError(f"Set the {var_name} environment variable")


def get_daily_task_hours(db, user_name):
    """
    Get daily task hours summary for a specific user.
    Returns task owner, close date, and total time spent for each day.
    
    Args:
        db: Database connection
        user_name: Username to filter activities
    Returns:
        List of tuples containing (Task_Owner, Task_Close_Date, Daily_Task_Hours)
    """
    if not user_name:
        print("Warning: user_name is empty")
        return []
    
    query = """
        SELECT a.Task_Owner, date(a.Task_Close_Date) as Task_Close_Date, 
               CAST(SUM(a.Time_Spent_On_Task) AS FLOAT) as Daily_Task_Hours 
        FROM Task_Ticket a
        WHERE a.Task_Owner IS NOT NULL 
        AND a.Task_Close_date IS NOT NULL 
        AND a.Task_Owner = ?
        GROUP BY a.Task_Owner, date(a.Task_Close_date)
        ORDER BY Task_Close_date DESC
        LIMIT 30
    """
    
    try:
        results = db.execute_query(query, (user_name,))
        return results
    except Exception as e:
        print(f"Error in get_daily_task_hours: {str(e)}")
        return []


def get_task_type_distribution(db, user_name, start_date, end_date):
    """
    Get the distribution of time spent across different task types for a user within a date range.
    Returns the percentage of time spent on each task type relative to total time.
    
    Args:
        db: Database connection
        user_name: Username to filter activities
        start_date: Start date for the period (format: 'YYYY-MM-DD')
        end_date: End date for the period (format: 'YYYY-MM-DD')
    Returns:
        List of tuples containing (Task_Type, Time_Percentage)
    """
    if not all([user_name, start_date, end_date]):
        print("Warning: missing required parameters")
        return []
    

    query = """
            SELECT 
                Task_Type, 
                ROUND((total_spented_hours * 1.0) / total * 100, 2) / 100.0 AS time_percentage
            FROM (
                SELECT 
                    a.Task_Owner, 
                    a.Task_Type,
                    SUM(a.Time_Spent_On_Task) AS total_spented_hours,
                    (
                        SELECT SUM(b.Time_Spent_On_Task) 
                        FROM Task_Ticket AS b
                        WHERE 
                            b.task_owner IS NOT NULL 
                            AND b.Task_Close_date BETWEEN ? AND ?
                            AND b.Task_Owner = a.Task_Owner
                    ) AS total
                FROM Task_Ticket AS a
                WHERE 
                    a.task_owner IS NOT NULL 
                    AND a.Task_Close_date BETWEEN ? AND ?
                    AND a.Task_Owner = ?
                GROUP BY a.task_owner, a.Task_Type
            )
            WHERE total > 0
            ORDER BY time_percentage DESC
        """
    try:
        # Parameters are used twice in the query (for both subquery and main query)
        params = (start_date, end_date, start_date, end_date, user_name)
        results = db.execute_query(query, params)
        
        if not results:
            print("No task distribution data found")
            return []
            
        processed_results = []
        
        for row in results:
            task_type = str(row[0]) if row[0] is not None else 'Unknown'
            try:
                # The percentage is already calculated in the SQL query
                percentage = float(row[1]) if row[1] is not None else 0.0
                percentage = max(0.0, min(1.0, percentage))  # Ensure value is between 0 and 1
            except (TypeError, ValueError) as e:
                print(f"Error processing percentage for {task_type}: {e}")
                percentage = 0.0
                
            processed_results.append((task_type, percentage))
        
        return processed_results
        
    except Exception as e:
        print(f"Error in get_task_type_distribution: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def get_user_activity_summary(db, start_date=None, end_date=None, user_name=None):
    
    
    query = """
                select distinct task_owner
                from Task_Ticket
                where Task_Close_date between ? and ?
            """
    
    try:        # Use positional parameters
        params = (start_date, end_date)
        
        # Debug: Print the query with parameters
        print(f"Executing query with parameters: {params}")
        
        results = db.execute_query(query, params)
        
        # Debug: Print results
        if results:
            print(f"Query returned {len(results)} rows")
            for row in results[:3]:  # Print first 3 rows as sample
                print(f"Sample row: {row}")
        else:
            print("Query returned no results")
            
        return results
    except Exception as e:
        print(f"Error in get_user_activity_summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
