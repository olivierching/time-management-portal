from flask import render_template, request, redirect, url_for, session, flash, jsonify
from dbQueryPassword import verify_current_password, update_user_password
from dbQueryLoginAccount import get_user_by_id, get_all_users, create_user, update_user, delete_user, get_user_by_login
from dbconnecter import DBConnecter
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'Time_Management_Portal_DB.db')

def register_user_routes(app):
    @app.route('/change-password', methods=['GET', 'POST'])
    def change_password():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate inputs
            if not all([current_password, new_password, confirm_password]):
                flash('All fields are required', 'error')
                return redirect(url_for('change_password'))
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('change_password'))
            
            # Verify current password and update
            try:
                db = DBConnecter(DATABASE_URL)
                if not verify_current_password(db, session['username'], current_password):
                    flash('Current password is incorrect', 'error')
                    db.close()
                    return redirect(url_for('change_password'))
                
                success, message = update_user_password(db, session['username'], new_password)
                db.close()
                
                if success:
                    flash('Password changed successfully', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash(message, 'error')
                    return redirect(url_for('change_password'))
                    
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'error')
                return redirect(url_for('change_password'))
        
        return render_template('change_password.html')

    @app.route('/users')
    def users():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        # Check if user is administrator
        if session.get('account_type') != 'Administrator':
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('dashboard'))
        
        # Get filter parameters
        username_filter = request.args.get('username', '')
        account_type_filter = request.args.get('account_type', '')
        
        try:
            db = DBConnecter(DATABASE_URL)
            
            # Get all account types for dropdown
            account_types = db.execute_query("SELECT ID, Description FROM Account_Type ORDER BY Description")
            
            # Build query based on filters
            query = """
                SELECT u.ID, u.Login_Name, u.Full_Name, u.First_Name, u.Last_Name, u.Email,
                       (SELECT Description FROM Account_Type WHERE ID = u.Account_Type_ID) as Account_Type
                FROM Login_Account u
                WHERE 1=1
            """
            params = []
            
            if username_filter:
                query += " AND (u.Login_Name LIKE ? OR u.Full_Name LIKE ?)"
                params.extend([f"%{username_filter}%", f"%{username_filter}%"])
            
            if account_type_filter:
                query += " AND u.Account_Type_ID = ?"
                params.append(account_type_filter)
            
            query += " ORDER BY u.Full_Name"
            
            users_list = db.execute_query(query, params)
            db.close()
            
            return render_template('user_management.html', 
                                 users=users_list or [], 
                                 account_types=account_types or [])
        except Exception as e:
            flash(f'Error retrieving users: {str(e)}', 'error')
            return render_template('user_management.html', users=[], account_types=[])

    @app.route('/get_user/<user_id>')
    def get_user(user_id):
        if 'username' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        if session.get('account_type') != 'Administrator':
            return jsonify({'error': 'Access denied'}), 403
        
        try:
            db = DBConnecter(DATABASE_URL)
            user = get_user_by_id(db, user_id)
            db.close()
            
            if user:
                user_data = {
                    'ID': user[0],
                    'Account_Type_ID': user[1],
                    'Login_Name': user[2],
                    'First_Name': user[3],
                    'Last_Name': user[4],
                    'Full_Name': user[5],
                    'Email': user[6]
                }
                return jsonify(user_data)
            return jsonify({'error': 'User not found'}), 404
        except Exception as e:
            app.logger.error(f"Error fetching user: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/create_user', methods=['POST'])
    def create_user_route():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        if session.get('account_type') != 'Administrator':
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('users'))
        
        account_type_id = request.form.get('account_type_id')
        login_name = request.form.get('login_name')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate required fields
        if not all([account_type_id, login_name, first_name, last_name, email, password]):
            flash('All fields are required for new users', 'error')
            return redirect(url_for('users'))
        
        try:
            db = DBConnecter(DATABASE_URL)
            
            # Check if username already exists
            existing_user = get_user_by_login(db, login_name)
            if existing_user:
                flash('Username already exists', 'error')
                db.close()
                return redirect(url_for('users'))
            
            # Create new user
            create_user(db, account_type_id, login_name, first_name, last_name, email, password)
            flash('User created successfully!', 'success')
            db.close()
            
        except Exception as e:
            flash(f'Error creating user: {str(e)}', 'error')
        
        return redirect(url_for('users'))

    @app.route('/update_user', methods=['POST'])
    def update_user_route():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        if session.get('account_type') != 'Administrator':
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('users'))
        
        user_id = request.form.get('userId')
        account_type_id = request.form.get('account_type_id')
        login_name = request.form.get('login_name')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate required fields
        if not all([user_id, account_type_id, login_name, first_name, last_name, email]):
            flash('All fields except password are required', 'error')
            return redirect(url_for('users'))
        
        try:
            db = DBConnecter(DATABASE_URL)
            
            # Check if username already exists for different user
            existing_user = get_user_by_login(db, login_name)
            if existing_user and str(existing_user[0]) != str(user_id):
                flash('Username already exists for another user', 'error')
                db.close()
                return redirect(url_for('users'))
            
            # Prepare update data
            update_data = {
                'account_type_id': account_type_id,
                'login_name': login_name,
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }
            
            # Only include password if provided
            if password:
                update_data['password'] = password
            
            # Update user
            update_user(db, user_id, **update_data)
            flash('User updated successfully!', 'success')
            db.close()
            
        except Exception as e:
            flash(f'Error updating user: {str(e)}', 'error')
        
        return redirect(url_for('users'))

    @app.route('/delete_user', methods=['POST'])
    def delete_user_route():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        if session.get('account_type') != 'Administrator':
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('users'))
        
        user_id = request.form.get('userId')
        
        if not user_id:
            flash('User ID is required', 'error')
            return redirect(url_for('users'))
        
        try:
            db = DBConnecter(DATABASE_URL)
            
            # Prevent users from deleting themselves
            current_user = get_user_by_login(db, session['username'])
            if current_user and str(current_user[0]) == str(user_id):
                flash('You cannot delete your own account', 'error')
                db.close()
                return redirect(url_for('users'))
            
            # Delete user
            delete_user(db, user_id)
            flash('User deleted successfully!', 'success')
            db.close()
            
        except Exception as e:
            flash(f'Error deleting user: {str(e)}', 'error')
        
        return redirect(url_for('users'))
