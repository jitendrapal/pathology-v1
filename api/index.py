"""
Vercel serverless function entry point
This file is required for Vercel deployment
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variable for serverless
os.environ['VERCEL'] = '1'

try:
    from app import app, create_tables

    # Initialize database tables on cold start
    # Note: On Vercel, SQLite is ephemeral and will reset on each deployment
    try:
        with app.app_context():
            create_tables()
            print("✅ Database initialized for serverless environment")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize database: {e}")
        # Continue anyway - the app might still work for some routes

    # Export the Flask app for Vercel
    # Vercel will use this as the WSGI application
    app = app

except Exception as e:
    print(f"❌ Critical error loading application: {e}")
    import traceback
    traceback.print_exc()

    # Create a minimal error app
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def error():
        return f"Application failed to load: {str(e)}", 500

