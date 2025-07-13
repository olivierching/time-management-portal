from flask import render_template, request, redirect, url_for, session, flash, jsonify
from dbQueryChange import get_change_details, get_single_change, update_change, create_task_from_change
from dbconnecter import DBConnecter
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'Time_Management_Portal_DB.db')

def register_change_routes(app):
    @app.route('/changes')
    def changes():
        if 'username' not in session:
            return redirect(url_for('login'))

        
        # Get filter parameters
        filters = {}
        if request.args.get('ticket_id'):
            filters['ticket_id'] = request.args.get('ticket_id')
        if request.args.get('change_state'):
            filters['change_state'] = request.args.get('change_state')
        if request.args.get('date_from'):
            filters['date_from'] = request.args.get('date_from')
        if request.args.get('date_to'):
            filters['date_to'] = request.args.get('date_to')
        
        print(f"User is change_state: {request.args.get('change_state')}")
        print(f"Filters: {filters}")

        try:
            db = DBConnecter(DATABASE_URL)
            # Show all changes if any filter is applied
            print(f"Filters: {bool(filters)}")

            show_all = bool(filters)

            changes = get_change_details(db, session['full_name'], filters if filters else None, show_all)
            db.close()
            return render_template('change.html', changes=changes)
        except Exception as e:
            flash(f'Error retrieving changes: {str(e)}', 'error')
            return render_template('change.html', changes=[])

    @app.route('/get_change/<ticket_id>')
    def get_change(ticket_id):
        if 'username' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            db = DBConnecter(DATABASE_URL)
            change = get_single_change(db, ticket_id)
            db.close()
            
            if change:
                return jsonify(change)
            return jsonify({'error': 'Change not found'}), 404
        except Exception as e:
            app.logger.error(f"Error fetching change: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/update_change', methods=['POST'])
    def update_change_route():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        ticket_id = request.form.get('ticketId')
        change_data = {
            'Change_Ticket_ID': request.form.get('change_ticket_id'),
            'Impact_Service': request.form.get('impact_service'),
            'Task_name': request.form.get('task_name'),
            'Change_state': request.form.get('change_state'),
            'Request_Ticket_ID': request.form.get('request_ticket_id'),
            'Task_Start_Date': request.form.get('task_start_date'),
            'Task_End_Date': request.form.get('task_end_date') or None,
            'Time_Spent': request.form.get('time_spent'),
            'Assignment_Group': request.form.get('assignment_group'),
            'Request_By': request.form.get('request_by'),
            'Change_Delegation': request.form.get('change_delegation')
        }
        
        db = DBConnecter(DATABASE_URL)
        try:
            update_change(db, ticket_id, **change_data)
            flash('Change updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating change: {str(e)}', 'error')
        finally:
            db.close()
        
        return redirect(url_for('changes'))

    @app.route('/create_task_for_change', methods=['POST'])
    def create_task_from_change_route():
        if 'username' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401

        try:
            data = request.get_json()
            if not data or not data.get('ticket_id'):
                return jsonify({'success': False, 'error': 'Missing change ticket ID'}), 400

            app.logger.info(f"Creating task for change ticket: {data['ticket_id']}")
            
            db = DBConnecter(DATABASE_URL)
            
            # Call the function to create a task from the change ticket
            success, message = create_task_from_change(db, session['full_name'], data['ticket_id'])
            db.close()
            
            app.logger.info(f"Task creation result: success={success}, message={message}")
            
            if success:
                return jsonify({'success': True, 'message': message})
            else:
                return jsonify({'success': False, 'error': message}), 500

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
