def get_team_workload(db):
    """Get the current workload distribution across team members."""
    query = """
    SELECT 
        la.Login_Name,
        COUNT(DISTINCT t.Task_ID) as active_tasks,
        SUM(t.Estimated_Hours) as total_estimated_hours
    FROM Login_Account la
    LEFT JOIN Task t ON la.Login_Name = t.Assigned_To
    WHERE t.Status != 'Completed'
    GROUP BY la.Login_Name
    ORDER BY total_estimated_hours DESC
    """
    
    return db.execute_query(query)

def get_average_daily_hours(db):
    """Get the average daily hours worked by each team member."""
    query = """
    SELECT 
        la.Login_Name,
        AVG(t.Hours_Worked) as avg_daily_hours
    FROM Login_Account la
    LEFT JOIN Time_Entry t ON la.Login_Name = t.Login_Name
    GROUP BY la.Login_Name
    ORDER BY avg_daily_hours DESC
    """
    
    return db.execute_query(query)

def get_task_type_distribution(db, username=None, start_date=None, end_date=None):
    """Get the distribution of task types across the team or for a specific user.
    
    Args:
        db: Database connection
        username: Optional username to filter tasks for a specific user
        start_date: Optional start date for date range filtering
        end_date: Optional end date for date range filtering
    """
    base_query = """
    SELECT 
        Task_Type,
        COUNT(*) as task_count
    FROM Task
    WHERE 1=1
    """
    params = []
    
    if username:
        base_query += " AND Assigned_To = ?"
        params.append(username)
    
    if start_date:
        base_query += " AND Created_Date >= ?"
        params.append(start_date)
    
    if end_date:
        base_query += " AND Created_Date <= ?"
        params.append(end_date)
    
    base_query += """
    GROUP BY Task_Type
    ORDER BY task_count DESC
    """
    
    return db.execute_query(base_query, tuple(params))

def get_team_completion_rate(db, days=30):
    """Get the task completion rate for each team member in the last X days."""
    query = """
    SELECT 
        la.Login_Name,
        COUNT(CASE WHEN t.Status = 'Completed' THEN 1 END) as completed_tasks,
        COUNT(*) as total_tasks
    FROM Login_Account la
    LEFT JOIN Task t ON la.Login_Name = t.Assigned_To
    WHERE t.Created_Date >= date('now', ?)
    GROUP BY la.Login_Name
    """
    
    cursor = db.get_cursor()
    result = cursor.execute(query, (f'-{days} days',))
    return result.fetchall()