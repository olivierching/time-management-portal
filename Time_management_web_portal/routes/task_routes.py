from flask import render_template, request, redirect, url_for, session, flash, jsonify
from dbQueryTask import task_type, get_task_sub_types, get_task_details, get_single_task, create_task, update_task, delete_task
from dbconnecter import DBConnecter
from datetime import datetime
from sympy import false
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'Time_Management_Portal_DB.db')

def register_task_routes(app):
    @app.route('/tasks')
    def tasks():
        if 'username' not in session:
            return redirect(url_for('login'))

        # Get filter parameters
        filters = {}

        if session['account_type'] != 'Administrator':
            # If the user is not an admin, filter tasks by the logged-in user's full name
            filters['task_owner'] = session['full_name']    

        # Handle ticket ID filter
        if request.args.get('ticket_id'):
            filters['ticket_id'] = request.args.get('ticket_id')
        
        # Handle task type filter
        if request.args.get('task_type'):
            filters['task_type'] = request.args.get('task_type')
        
        # Handle sub type filter
        if request.args.get('sub_type'):
            filters['sub_type'] = request.args.get('sub_type')
        
        print(f"Request args: {request.args.get('status')}")
        # Handle status filter
        if request.args.get('status'):
            filters['status'] = request.args.get('status')

        # Handle date filters
        if request.args.get('date_from'):
            filters['date_from'] = request.args.get('date_from')

        if request.args.get('date_to'):
            filters['date_to'] = request.args.get('date_to')
        
        try:
            db = DBConnecter(DATABASE_URL)
            tasks_list = get_task_details(db, filters if filters else None, show_all=false)
            task_types_list = task_type(db)
            sub_types = None
            
            if request.args.get('task_type'):
                sub_types = get_task_sub_types(db, request.args.get('task_type'))
            
            db.close()
            return render_template('task.html', 
                                 tasks=tasks_list, 
                                 task_types=task_types_list, 
                                 sub_types=sub_types)
        except Exception as e:
            flash(f'Error retrieving tasks: {str(e)}', 'error')
            return render_template('task.html', 
                                 tasks=[], 
                                 task_types=[], 
                                 sub_types=[])

    @app.route('/get_task/<ticket_id>')
    def get_task(ticket_id):
        if 'username' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            db = DBConnecter(DATABASE_URL)
            task = get_single_task(db, ticket_id)
            db.close()
            
            if task:
                return jsonify(task)
            return jsonify({'error': 'Task not found'}), 404
        except Exception as e:
            app.logger.error(f"Error fetching task: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/get_task_sub_types/<task_type>')
    def get_subtypes(task_type):
        if 'username' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            db = DBConnecter(DATABASE_URL)
            sub_types = get_task_sub_types(db, task_type)
            db.close()
            
            return jsonify({'sub_types': sub_types})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/update_task', methods=['POST'])
    def update_task_route():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        task_type = request.form.get('task_type')
        task_sub_type = request.form.get('task_sub_type')
        task_id = request.form.get('taskId')  # This is the ID field
        task_create_date = request.form.get('task_create_date')
        time_spent = float(request.form.get('time_spent', 0))
        description = request.form.get('description')
        status = request.form.get('status')
        task_close_date = request.form.get('task_close_date')
        ticket_id = request.form.get('ticket_id')  # Get the Ticket ID field
        
        # If status is changed to Closed and no close date is provided, set it to current date
        if status == 'Closed' and not task_close_date:
            task_close_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        db = DBConnecter(DATABASE_URL)
        print(f"Updating task with ID: {task_id}, type: {task_type}, sub-type: {task_sub_type}, status: {status}, close date: {task_close_date}")

        try:
            update_task(
                db=db,        
                task_id=task_id,
                task_type=task_type,
                task_sub_type=task_sub_type,    
                task_create_date=task_create_date,
                time_spent=time_spent,
                description=description,
                status=status,
                task_close_date=task_close_date,
                ticket_id=ticket_id  # Pass the ticket ID to update function
            )
            flash('Task updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating task: {str(e)}', 'error')
        finally:
            db.close()
        
        return redirect(url_for('tasks'))

    @app.route('/create_task', methods=['POST'])
    def create_task_route():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        task_type = request.form.get('task_type')
        task_sub_type = request.form.get('task_sub_type')
        description = request.form.get('description')
        time_spent = float(request.form.get('time_spent', 0))
        task_create_date = request.form.get('task_create_date')  # This will be None if not provided
        task_close_date = request.form.get('task_close_date')  # This will be None if not provided
        status = request.form.get('status', 'Open')  # Default to 'Open' if not provided
        ticket_id = request.form.get('ticket_id')  # New Ticket ID field
        db = DBConnecter(DATABASE_URL)
        try:
            create_task(
                db=db,            
                task_type=task_type,
                task_sub_type=task_sub_type,
                ticket_id=ticket_id,
                description=description,
                task_owner=session['full_name'],  # Use the logged-in user's full name as the task owner
                time_spent=time_spent,
                task_create_date=task_create_date,
                task_close_date=task_close_date,
                status=status,
                
            )
            flash('Task created successfully!', 'success')
        except Exception as e:
            flash(f'Error creating task: {str(e)}', 'error')
        finally:
            db.close()
        
        return redirect(url_for('tasks'))

    @app.route('/delete_task/<task_id>', methods=['POST'])
    def delete_task_route(task_id):
        if 'username' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        try:
            db = DBConnecter(DATABASE_URL)
            delete_task(db, task_id)
            db.close()
            
            return jsonify({'success': True, 'message': 'Task deleted successfully'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
