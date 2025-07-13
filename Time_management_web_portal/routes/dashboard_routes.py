from flask import render_template, request, redirect, url_for, session, flash
from dbQueryDashboard import get_daily_task_hours
import dbQueryDashboard as dashboard_queries
from dbQueryLoginAccount import get_users_name
from dbconnecter import DBConnecter
from datetime import datetime, timedelta
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'Time_Management_Portal_DB.db')

def register_dashboard_routes(app):
    @app.route('/dashboard')
    def dashboard():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        try:
            db = DBConnecter(DATABASE_URL)
            # Get daily task hours
            daily_task_hours = get_daily_task_hours(db, session.get('full_name'))
            # Calculate date range for task distribution (last 30 days)
            today = datetime.now()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            end_date = end_date.strftime('%Y-%m-%d')
            print(f"Start date: {start_date}, End date: {end_date}")
            # Get task type distribution
            task_type_distribution = dashboard_queries.get_task_type_distribution(
                db, 
                session.get('full_name'),
                start_date,
                end_date
            )        
            print(f"Task type distribution: {task_type_distribution}")
            # Get all users' activity data
            users = get_users_name(db)
            
            db.close()
            
            return render_template('dashboard.html',
                                 daily_task_hours=daily_task_hours,
                                 task_type_distribution=task_type_distribution,
                                 start_date=start_date,
                                 end_date=end_date
                                 )
        except Exception as e:
            flash(f'Error loading dashboard data: {str(e)}', 'error')
            return render_template('dashboard.html',
                                 daily_task_hours=[],
                                 task_type_distribution=[])
