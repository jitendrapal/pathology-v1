#!/usr/bin/env python3
"""
Production Web-Based SQLite Database Viewer for Digital Ocean
Optimized for server deployment with proper security
"""

from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for, flash
import sqlite3
import os
import json
from datetime import datetime
import pandas as pd
import io
import logging
from logging.handlers import RotatingFileHandler

# Create production Flask app
prod_db_viewer_app = Flask(__name__, template_folder='templates')
prod_db_viewer_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-secret-key-in-production')

# Production configuration
ADMIN_USERNAME = os.environ.get('DB_ADMIN_USER', 'admin')
ADMIN_PASSWORD = os.environ.get('DB_ADMIN_PASS', 'pathology123')
DEBUG_MODE = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
PORT = int(os.environ.get('FLASK_PORT', 5001))

class ProductionWebDatabaseViewer:
    def __init__(self, db_path=None):
        if db_path is None:
            # Production database path
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            self.db_path = os.path.join(data_dir, 'pathology.db')
        else:
            self.db_path = db_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Get database connection with timeout"""
        if os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute('PRAGMA journal_mode=WAL;')  # Better for concurrent access
            return conn
        return None
    
    def get_database_info(self):
        """Get database information"""
        try:
            if not os.path.exists(self.db_path):
                return {"error": "Database file not found"}
            
            conn = self.get_connection()
            if not conn:
                return {"error": "Database connection failed"}
            
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
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    table_info[table_name] = count
                except Exception as e:
                    table_info[table_name] = f"Error: {str(e)}"
            
            conn.close()
            
            return {
                "path": os.path.basename(self.db_path),
                "size_mb": round(file_size / (1024 * 1024), 2),
                "last_modified": file_time.strftime('%Y-%m-%d %H:%M:%S'),
                "tables": table_info,
                "total_tables": len(tables),
                "server_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            prod_db_viewer_app.logger.error(f"Database info error: {str(e)}")
            return {"error": str(e)}
    
    def get_table_data(self, table_name, limit=100, offset=0):
        """Get data from specific table with error handling"""
        try:
            conn = self.get_connection()
            if not conn:
                return {"error": "Database connection failed"}
            
            cursor = conn.cursor()
            
            # Validate table name (security)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
            if not cursor.fetchone():
                return {"error": "Table not found"}
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            total_count = cursor.fetchone()[0]
            
            # Get data with pagination
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?;", (limit, offset))
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
            prod_db_viewer_app.logger.error(f"Table data error for {table_name}: {str(e)}")
            return {"error": str(e)}
    
    def get_real_time_stats(self):
        """Get real-time database statistics"""
        try:
            conn = self.get_connection()
            if not conn:
                return {"error": "Database connection failed"}
            
            cursor = conn.cursor()
            stats = {}
            
            # Safe queries with error handling
            try:
                cursor.execute("SELECT COUNT(*) FROM patient;")
                stats['total_patients'] = cursor.fetchone()[0]
            except:
                stats['total_patients'] = 0
            
            try:
                cursor.execute("SELECT COUNT(*) FROM patient WHERE date_registered >= date('now', '-7 days');")
                stats['new_patients_week'] = cursor.fetchone()[0]
            except:
                stats['new_patients_week'] = 0
            
            try:
                cursor.execute("SELECT COUNT(*) FROM patient_test;")
                stats['total_tests'] = cursor.fetchone()[0]
            except:
                stats['total_tests'] = 0
            
            try:
                cursor.execute("SELECT COUNT(*) FROM patient_test WHERE status = 'Pending';")
                stats['pending_tests'] = cursor.fetchone()[0]
            except:
                stats['pending_tests'] = 0
            
            try:
                cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM payment;")
                stats['total_revenue'] = cursor.fetchone()[0]
            except:
                stats['total_revenue'] = 0
            
            try:
                cursor.execute("SELECT COALESCE(SUM(remaining_amount), 0) FROM patient_bill WHERE remaining_amount > 0;")
                stats['pending_payments'] = cursor.fetchone()[0]
            except:
                stats['pending_payments'] = 0
            
            stats['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            stats['server_status'] = 'online'
            
            conn.close()
            return stats
        except Exception as e:
            prod_db_viewer_app.logger.error(f"Stats error: {str(e)}")
            return {"error": str(e)}

# Initialize production viewer
prod_viewer = ProductionWebDatabaseViewer()

def login_required(f):
    """Decorator to require login for routes"""
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@prod_db_viewer_app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with production styling"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            session['login_time'] = datetime.now().isoformat()
            prod_db_viewer_app.logger.info(f"User {username} logged in from {request.remote_addr}")
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            prod_db_viewer_app.logger.warning(f"Failed login attempt for {username} from {request.remote_addr}")
            flash('Invalid username or password!', 'error')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pathology Lab Database - Secure Access</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .login-card { box-shadow: 0 10px 30px rgba(0,0,0,0.3); border: none; border-radius: 15px; }
        </style>
    </head>
    <body class="d-flex align-items-center">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-4">
                    <div class="card login-card">
                        <div class="card-header bg-primary text-white text-center">
                            <h4><i class="fas fa-database me-2"></i>Pathology Lab</h4>
                            <p class="mb-0">Database Viewer - Secure Access</p>
                        </div>
                        <div class="card-body p-4">
                            <form method="POST">
                                <div class="mb-3">
                                    <label class="form-label"><i class="fas fa-user me-2"></i>Username</label>
                                    <input type="text" name="username" class="form-control" required autofocus>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label"><i class="fas fa-lock me-2"></i>Password</label>
                                    <input type="password" name="password" class="form-control" required>
                                </div>
                                <div class="d-grid">
                                    <button type="submit" class="btn btn-primary">
                                        <i class="fas fa-sign-in-alt me-2"></i>Login
                                    </button>
                                </div>
                            </form>
                        </div>
                        <div class="card-footer text-center bg-light">
                            <small class="text-muted">
                                <i class="fas fa-shield-alt me-1"></i>Secure Database Access
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@prod_db_viewer_app.route('/logout')
def logout():
    """Logout with logging"""
    username = session.get('username', 'Unknown')
    prod_db_viewer_app.logger.info(f"User {username} logged out")
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@prod_db_viewer_app.route('/')
@login_required
def index():
    """Main database viewer page"""
    return render_template('database_viewer.html')

@prod_db_viewer_app.route('/api/database-info')
@login_required
def api_database_info():
    """API endpoint for database information"""
    return jsonify(prod_viewer.get_database_info())

@prod_db_viewer_app.route('/api/table-data/<table_name>')
@login_required
def api_table_data(table_name):
    """API endpoint for table data"""
    limit = min(int(request.args.get('limit', 100)), 1000)  # Max 1000 records
    offset = int(request.args.get('offset', 0))
    return jsonify(prod_viewer.get_table_data(table_name, limit, offset))

@prod_db_viewer_app.route('/api/real-time-stats')
@login_required
def api_real_time_stats():
    """API endpoint for real-time database statistics"""
    return jsonify(prod_viewer.get_real_time_stats())

@prod_db_viewer_app.route('/api/export/<table_name>')
@login_required
def api_export_table(table_name):
    """API endpoint for exporting table data"""
    try:
        conn = prod_viewer.get_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"})
        
        # Validate table name
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        if not cursor.fetchone():
            return jsonify({"error": "Table not found"})
        
        # Get data
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        
        # Create CSV
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        csv_data = io.BytesIO()
        csv_data.write(output.getvalue().encode('utf-8'))
        csv_data.seek(0)
        
        # Log export
        username = session.get('username', 'Unknown')
        prod_db_viewer_app.logger.info(f"User {username} exported table {table_name}")
        
        return send_file(
            csv_data,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{table_name}_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        prod_db_viewer_app.logger.error(f"Export error for {table_name}: {str(e)}")
        return jsonify({"error": str(e)})

# Setup logging for production
if not DEBUG_MODE:
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = RotatingFileHandler('logs/database_viewer.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    prod_db_viewer_app.logger.addHandler(file_handler)
    prod_db_viewer_app.logger.setLevel(logging.INFO)
    prod_db_viewer_app.logger.info('Database viewer startup')

if __name__ == '__main__':
    print("🌐 Starting Production Web Database Viewer...")
    print(f"📁 Database: {prod_viewer.db_path}")
    print(f"🔐 Authentication: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    print(f"🔗 Host: {HOST}:{PORT}")
    print(f"🛡️ Debug Mode: {DEBUG_MODE}")
    print(f"📊 Production-ready database viewer!")
    
    # Run with production settings
    prod_db_viewer_app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG_MODE,
        threaded=True
    )
