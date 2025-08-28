#!/usr/bin/env python3
"""
Web-Based SQLite Database Viewer
Access SQLite database through web browser from anywhere
"""

from flask import Flask, render_template, jsonify, request, send_file
import sqlite3
import os
import json
from datetime import datetime
import pandas as pd
import io

# Create separate Flask app for database viewer
db_viewer_app = Flask(__name__, template_folder='templates')
db_viewer_app.config['SECRET_KEY'] = 'database-viewer-secret-key'

class WebDatabaseViewer:
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
    
    def search_table(self, table_name, search_term, limit=100):
        """Search data in table"""
        try:
            conn = self.get_connection()
            if not conn:
                return {"error": "Database connection failed"}
            
            cursor = conn.cursor()
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            
            # Build search query
            search_conditions = []
            for col in columns:
                search_conditions.append(f"{col} LIKE ?")
            
            search_query = f"SELECT * FROM {table_name} WHERE {' OR '.join(search_conditions)} LIMIT {limit};"
            search_params = [f"%{search_term}%"] * len(columns)
            
            cursor.execute(search_query, search_params)
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
                "search_term": search_term,
                "result_count": len(formatted_rows)
            }
        except Exception as e:
            return {"error": str(e)}

# Initialize viewer
viewer = WebDatabaseViewer()

@db_viewer_app.route('/')
def index():
    """Main database viewer page"""
    return render_template('database_viewer.html')

@db_viewer_app.route('/api/database-info')
def api_database_info():
    """API endpoint for database information"""
    return jsonify(viewer.get_database_info())

@db_viewer_app.route('/api/table-data/<table_name>')
def api_table_data(table_name):
    """API endpoint for table data"""
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    return jsonify(viewer.get_table_data(table_name, limit, offset))

@db_viewer_app.route('/api/search/<table_name>')
def api_search_table(table_name):
    """API endpoint for searching table"""
    search_term = request.args.get('q', '')
    limit = int(request.args.get('limit', 100))
    return jsonify(viewer.search_table(table_name, search_term, limit))

@db_viewer_app.route('/api/export/<table_name>')
def api_export_table(table_name):
    """API endpoint for exporting table data"""
    try:
        conn = viewer.get_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"})
        
        # Get all data
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        
        # Create CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        # Convert to bytes
        csv_data = io.BytesIO()
        csv_data.write(output.getvalue().encode('utf-8'))
        csv_data.seek(0)
        
        return send_file(
            csv_data,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{table_name}_export.csv'
        )
    except Exception as e:
        return jsonify({"error": str(e)})

@db_viewer_app.route('/api/real-time-stats')
def api_real_time_stats():
    """API endpoint for real-time database statistics"""
    try:
        conn = viewer.get_connection()
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
        
        cursor.execute("SELECT COUNT(*) FROM patient_test WHERE status = 'Completed';")
        stats['completed_tests'] = cursor.fetchone()[0]
        
        # Payment stats
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM payment;")
        stats['total_revenue'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(SUM(remaining_amount), 0) FROM patient_bill WHERE remaining_amount > 0;")
        stats['pending_payments'] = cursor.fetchone()[0]
        
        # Recent activity
        cursor.execute("""
            SELECT 'Patient Registered' as activity, first_name || ' ' || last_name as details, date_registered as timestamp
            FROM patient 
            ORDER BY date_registered DESC 
            LIMIT 5
        """)
        recent_activity = []
        for row in cursor.fetchall():
            recent_activity.append({
                "activity": row[0],
                "details": row[1],
                "timestamp": row[2]
            })
        
        stats['recent_activity'] = recent_activity
        stats['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn.close()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("🌐 Starting Web Database Viewer...")
    print(f"📁 Database: {viewer.db_path}")
    print(f"🔗 Access URL: http://localhost:5001")
    print(f"🔗 Network URL: http://your-ip:5001")
    print("📊 Real-time database viewing available!")
    
    # Run on different port to avoid conflict with main app
    db_viewer_app.run(host='0.0.0.0', port=5001, debug=True)
