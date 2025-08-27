#!/usr/bin/env python3
"""
Database initialization script for production deployment
Run this script after deploying to create tables and load sample data
"""

import os
from app import app, db
from sample_data import create_sample_data

def init_database():
    """Initialize database tables and optionally load sample data"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if we should load sample data
        load_sample = os.environ.get('LOAD_SAMPLE_DATA', 'false').lower() == 'true'
        
        if load_sample:
            print("Loading sample data...")
            try:
                create_sample_data()
                print("Sample data loaded successfully!")
            except Exception as e:
                print(f"Error loading sample data: {e}")
                print("Database tables created but sample data not loaded.")
        else:
            print("Skipping sample data loading. Set LOAD_SAMPLE_DATA=true to load sample data.")

if __name__ == "__main__":
    init_database()
