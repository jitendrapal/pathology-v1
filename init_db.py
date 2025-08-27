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
        try:
            print("🔄 Initializing database...")

            # Import all models to ensure they're registered
            from models import Patient, Test, PatientTest, Hospital, SampleCollector, Payment, PatientBill
            print("✅ All models imported successfully")

            # Drop existing tables (for clean slate)
            print("🗑️ Dropping existing tables...")
            db.drop_all()

            # Create all tables
            print("🏗️ Creating database tables...")
            db.create_all()
            print("✅ All database tables created successfully!")

            # Verify tables exist
            try:
                tables = db.engine.table_names()
                print(f"📋 Created tables: {', '.join(tables)}")

                # Check specific tables
                required_tables = ['patient', 'test', 'patient_test', 'hospital', 'sample_collector', 'payment', 'patient_bill']
                missing_tables = []

                for table in required_tables:
                    if table in tables:
                        print(f"✅ {table} table created")
                    else:
                        print(f"❌ {table} table missing")
                        missing_tables.append(table)

                if missing_tables:
                    print(f"⚠️ Missing tables: {', '.join(missing_tables)}")
                    return False

            except Exception as e:
                print(f"⚠️ Could not verify tables: {e}")

            # Check if we should load sample data
            load_sample = os.environ.get('LOAD_SAMPLE_DATA', 'true').lower() == 'true'

            if load_sample:
                print("📊 Loading sample data...")
                try:
                    create_sample_data()
                    print("✅ Sample data loaded successfully!")
                except Exception as e:
                    print(f"❌ Error loading sample data: {e}")
                    print("Database tables created but sample data not loaded.")
                    return False
            else:
                print("⏭️ Skipping sample data loading. Set LOAD_SAMPLE_DATA=true to load sample data.")

            print("🎉 Database initialization completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    init_database()
