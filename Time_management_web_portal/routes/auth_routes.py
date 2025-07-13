from flask import render_template, request, redirect, url_for, session, flash
from dbQueryIncident import user_login_check
from dbconnecter import DBConnecter
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'Time_Management_Portal_DB.db')

def register_auth_routes(app):
    @app.route('/')
    def index():
        if 'username' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            db = DBConnecter(DATABASE_URL)
            id, account_type, full_name, status = user_login_check(db, username, password)
            db.close()
            
            if account_type:
                session['id'] = id
                session['username'] = username
                session['account_type'] = account_type
                session['full_name'] = full_name
                return redirect(url_for('dashboard'))
            else:
                error = status
        
        return render_template('login.html', error=error)

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        session.pop('account_type', None)
        return redirect(url_for('login'))
