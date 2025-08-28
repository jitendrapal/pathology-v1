#!/usr/bin/env python3
"""
Secure Web-Based SQLite Database Viewer with Authentication
Access SQLite database through web browser with login protection
"""

from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for, flash
import sqlite3
import os
import json
from datetime import datetime
import pandas as pd
import io
import hashlib

# Create secure Flask app for database viewer
secure_db_viewer_app = Flask(__name__, template_folder='templates')
secure_db_viewer_app.config['SECRET_KEY'] = 'secure-database-viewer-secret-key-change-in-production'

# Simple authentication (change these credentials)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'pathology123'  # Change this password!

class SecureWebDatabaseViewer:
    def __init__(self, db_path=None):
        if db_path is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            self.db_path = os.path.join(data_dir, 'pathology.db')
        else:
            self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        if os.path.exists(self.db_path):
            return sqlite3.connect(self.db_path)
        return None
    
    def get_database_info(self):
        """Get database information"""
        try:
            if not os.path.exists(self.db_path):
                return {"error": "Database file not found"}
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get file info
            file_size = os.path.getsize(self.db_path)
            file_time = datetime.fromtimestamp(os.path.getmtime(self.db_path))
            
            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = cursor.fetchall()
            
            table_info = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                table_info[table_name] = count
            
            conn.close()
            
            return {
                "path": self.db_path,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "last_modified": file_time.strftime('%Y-%m-%d %H:%M:%S'),
                "tables": table_info,
                "total_tables": len(tables)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_table_data(self, table_name, limit=100, offset=0):
        """Get data from specific table"""
        try:
            conn = self.get_connection()
            if not conn:
                return {"error": "Database connection failed"}
            
            cursor = conn.cursor()
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            total_count = cursor.fetchone()[0]
            
            # Get data with pagination
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset};")
            rows = cursor.fetchall()
            
            # Format data
            formatted_rows = []
            for row in rows:
                formatted_row = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if value is None:
                        formatted_row[col] = ""
                    else:
                        formatted_row[col] = str(value)
                formatted_rows.append(formatted_row)
            
            conn.close()
            
            return {
                "table_name": table_name,
                "columns": columns,
                "data": formatted_rows,
                "total_count": total_count,
                "current_page": (offset // limit) + 1,
                "total_pages": (total_count + limit - 1) // limit,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            return {"error": str(e)}

# Initialize secure viewer
secure_viewer = SecureWebDatabaseViewer()

def login_required(f):
    """Decorator to require login for routes"""
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@secure_db_viewer_app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('secure_index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Viewer - Login</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container">
            <div class="row justify-content-center mt-5">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header text-center">
                            <h4><i class="fas fa-database"></i> Database Viewer</h4>
                            <p class="text-muted">Secure Access</p>
                        </div>
                        <div class="card-body">
                            {% with messages = get_flashed_messages(with_categories=true) %}
                                {% if messages %}
                                    {% for category, message in messages %}
                                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}">{{ message }}</div>
                                    {% endfor %}
                                {% endif %}
                            {% endwith %}
                            <form method="POST">
                                <div class="mb-3">
                                    <label class="form-label">Username</label>
                                    <input type="text" name="username" class="form-control" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Password</label>
                                    <input type="password" name="password" class="form-control" required>
                                </div>
                                <div class="d-grid">
                                    <button type="submit" class="btn btn-primary">Login</button>
                                </div>
                            </form>
                        </div>
                        <div class="card-footer text-center">
                            <small class="text-muted">Pathology Lab Database Access</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@secure_db_viewer_app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@secure_db_viewer_app.route('/')
@login_required
def secure_index():
    """Main secure database viewer page"""
    return render_template('database_viewer.html')

@secure_db_viewer_app.route('/api/database-info')
@login_required
def api_database_info():
    """API endpoint for database information"""
    return jsonify(secure_viewer.get_database_info())

@secure_db_viewer_app.route('/api/table-data/<table_name>')
@login_required
def api_table_data(table_name):
    """API endpoint for table data"""
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    return jsonify(secure_viewer.get_table_data(table_name, limit, offset))

@secure_db_viewer_app.route('/api/real-time-stats')
@login_required
def api_real_time_stats():
    """API endpoint for real-time database statistics"""
    try:
        conn = secure_viewer.get_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"})
        
        cursor = conn.cursor()
        
        # Get real-time stats
        stats = {}
        
        # Patient stats
        cursor.execute("SELECT COUNT(*) FROM patient;")
        stats['total_patients'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patient WHERE date_registered >= date('now', '-7 days');")
        stats['new_patients_week'] = cursor.fetchone()[0]
        
        # Test stats
        cursor.execute("SELECT COUNT(*) FROM patient_test;")
        stats['total_tests'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patient_test WHERE status = 'Pending';")
        stats['pending_tests'] = cursor.fetchone()[0]
        
        # Payment stats
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM payment;")
        stats['total_revenue'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(SUM(remaining_amount), 0) FROM patient_bill WHERE remaining_amount > 0;")
        stats['pending_payments'] = cursor.fetchone()[0]
        
        stats['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stats['logged_in_user'] = session.get('username', 'Unknown')
        
        conn.close()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("🔒 Starting SECURE Web Database Viewer...")
    print(f"📁 Database: {secure_viewer.db_path}")
    print(f"🔐 Login Required: Username = {ADMIN_USERNAME}, Password = {ADMIN_PASSWORD}")
    print(f"🔗 Access URL: http://localhost:5002")
    print(f"🛡️ Secure database viewing with authentication!")
    
    # Run on different port with security
    secure_db_viewer_app.run(host='127.0.0.1', port=5002, debug=False)
