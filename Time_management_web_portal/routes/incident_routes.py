from flask import render_template, request, redirect, url_for, session, flash, jsonify
from dbQueryIncident import get_incident_details, get_single_incident, update_incident
from dbQueryLoginAccount import get_users_name
from dbQueryTask import create_task
from dbconnecter import DBConnecter
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'Time_Management_Portal_DB.db')

def register_incident_routes(app):
    @app.route('/incidents')
    def incidents():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        # Get filter parameters
        filters = {}
        if request.args.get('ticket_id'):
            filters['ticket_id'] = request.args.get('ticket_id')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('date_from'):
            filters['date_from'] = request.args.get('date_from')
        if request.args.get('date_to'):
            filters['date_to'] = request.args.get('date_to')
        
        try:
            db = DBConnecter(DATABASE_URL)
            # Determine if we should show all incidents
            show_all = bool(filters.get('status'))  # Show all if status filter is applied
            incidents = get_incident_details(db, session['full_name'], filters if filters else None, show_all)     
            db.close()
            return render_template('incident.html', incidents=incidents)
        except Exception as e:
            flash(f'Error retrieving incidents: {str(e)}', 'error')
            return render_template('incident.html', incidents=[])

    @app.route('/get_incident/<ticket_id>')
    def get_incident(ticket_id):
        if 'username' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            db = DBConnecter(DATABASE_URL)
            incident = get_single_incident(db, ticket_id)
            db.close()

            db = DBConnecter(DATABASE_URL)
            user_login_name = get_users_name(db)
            db.close()

            if incident:
                response = {
                    'incident': incident,
                    'user_login_name': user_login_name
                }
                return jsonify(response)
            return jsonify({'error': 'Incident not found'}), 404
        except Exception as e:
            app.logger.error(f"Error fetching incident: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/update_incident', methods=['POST'])
    def update_incident_route():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        ticket_id = request.form.get('ticketId')  # This is the ID field
        incident_ticket_id = request.form.get('incident_ticket_id')
        impact_service = request.form.get('impact_service')
        description = request.form.get('description')
        status = request.form.get('status')
        open_by = request.form.get('open_by')
        open_date = request.form.get('open_date')
        close_date = request.form.get('close_date') or None  # Convert empty string to None
        time_spent = request.form.get('time_spent')
        assign_group = request.form.get('assign_group')
        assign_to = request.form.get('assign_to')
        root_cause = request.form.get('root_cause')
        
        db = DBConnecter(DATABASE_URL)
        try:
            update_incident(
                db=db,
                ticket_id=ticket_id,
                ID=ticket_id,
                Incident_Ticket_ID=incident_ticket_id,
                Impact_Service=impact_service,
                Description=description,
                Status=status,
                Open_By=open_by,
                Open_Date=open_date,
                Close_Date=close_date,
                Time_Spent= time_spent, 
                Assign_Group=assign_group,
                Assign_to=assign_to,
                Root_Cause=root_cause
            )
            flash('Incident updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating incident: {str(e)}', 'error')
        finally:
            db.close()
        
        return redirect(url_for('incidents'))

    @app.route('/create_task_for_incident', methods=['POST'])
    def create_task_for_incident():
        if 'username' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        try:
            data = request.get_json()
            
            db = DBConnecter(DATABASE_URL)
            create_task(
                db=db,
                task_type=data['task_type'],
                task_sub_type=data['task_sub_type'],
                description=data['description'],
                task_owner=session['full_name'],  # Use the logged-in user's full name as the task owner
                task_create_date=data['task_create_date'],
                ticket_id=data['ticket_id'],
                status='Open'
            )
            db.close()
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error creating task: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
