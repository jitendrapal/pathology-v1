#!/usr/bin/env python3
"""
Startup script for DigitalOcean deployment
This script ensures database tables are created and sample data is loaded
"""

import os
import sys

def startup_database():
    """Initialize database for production deployment"""
    print("🚀 Starting database initialization...")
    
    try:
        # Import app and models
        from app import app, db
        from models import Patient, Test, PatientTest, Hospital, SampleCollector, Payment, PatientBill
        
        with app.app_context():
            print("🔄 Creating database tables...")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if tables exist
            try:
                tables = db.engine.table_names()
                print(f"📋 Created tables: {', '.join(tables)}")
                
                # Verify critical tables
                required_tables = ['patient', 'test', 'patient_test', 'payment', 'patient_bill']
                missing_tables = [table for table in required_tables if table not in tables]
                
                if missing_tables:
                    print(f"⚠️ Missing tables: {', '.join(missing_tables)}")
                else:
                    print("✅ All required tables created successfully!")
                    
            except Exception as e:
                print(f"⚠️ Could not verify tables: {e}")
            
            # Check if we need sample data
            try:
                patient_count = Patient.query.count()
                test_count = Test.query.count()
                
                print(f"📊 Current data: {patient_count} patients, {test_count} tests")
                
                if patient_count == 0 or test_count == 0:
                    print("📊 Loading sample data...")
                    
                    # Load sample data
                    from sample_data import create_sample_data
                    create_sample_data()
                    print("✅ Sample data loaded successfully!")
                else:
                    print("📊 Database already has data, skipping sample data loading")
                    
            except Exception as e:
                print(f"⚠️ Error checking/loading sample data: {e}")
                print("Database tables created but sample data may not be loaded")
        
        print("🎉 Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 PATHOLOGY LAB MANAGEMENT SYSTEM - STARTUP")
    print("=" * 60)
    
    success = startup_database()
    
    if success:
        print("\n✅ STARTUP COMPLETED SUCCESSFULLY!")
        print("🚀 Application is ready to serve requests")
    else:
        print("\n❌ STARTUP FAILED!")
        print("⚠️ Check the errors above and try again")
        sys.exit(1)
    
    print("=" * 60)
