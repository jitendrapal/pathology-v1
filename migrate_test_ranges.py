#!/usr/bin/env python3
"""
Migration script to add normal_range_min, normal_range_max, and unit columns to Test table
and populate them with sample data for existing tests.
"""

import sqlite3
import os

def migrate_test_table():
    """Add new columns to Test table and populate with sample data"""
    
    # Database path
    db_path = 'data/pathology.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the application first to create the database.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting Test table migration...")
        
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(test)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'normal_range_min' not in columns:
            print("➕ Adding normal_range_min column...")
            cursor.execute("ALTER TABLE test ADD COLUMN normal_range_min REAL DEFAULT 0.0")
        
        if 'normal_range_max' not in columns:
            print("➕ Adding normal_range_max column...")
            cursor.execute("ALTER TABLE test ADD COLUMN normal_range_max REAL DEFAULT 100.0")
        
        if 'unit' not in columns:
            print("➕ Adding unit column...")
            cursor.execute("ALTER TABLE test ADD COLUMN unit TEXT DEFAULT ''")
        
        # Sample data for common tests with their normal ranges and units
        test_ranges = {
            'Complete Blood Count (CBC)': {'min': 4.5, 'max': 5.5, 'unit': 'million/µL'},
            'Basic Metabolic Panel': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
            'Lipid Panel': {'min': 0, 'max': 200, 'unit': 'mg/dL'},
            'Urinalysis': {'min': 0, 'max': 0, 'unit': 'negative'},
            'Thyroid Function Test': {'min': 0.4, 'max': 4.0, 'unit': 'mIU/L'},
            'Liver Function Test': {'min': 7, 'max': 56, 'unit': 'U/L'},
            'Chest X-Ray': {'min': 0, 'max': 1, 'unit': 'normal'},
            'Stool Culture': {'min': 0, 'max': 0, 'unit': 'negative'},
            'Blood Sugar': {'min': 70, 'max': 140, 'unit': 'mg/dL'},
            'Hemoglobin': {'min': 12.0, 'max': 16.0, 'unit': 'g/dL'},
            'Platelet Count': {'min': 150, 'max': 450, 'unit': 'thousand/µL'},
            'Creatinine': {'min': 0.6, 'max': 1.2, 'unit': 'mg/dL'},
            'Urea': {'min': 15, 'max': 45, 'unit': 'mg/dL'},
            'Total Cholesterol': {'min': 0, 'max': 200, 'unit': 'mg/dL'},
            'HDL Cholesterol': {'min': 40, 'max': 100, 'unit': 'mg/dL'},
            'LDL Cholesterol': {'min': 0, 'max': 100, 'unit': 'mg/dL'},
            'Triglycerides': {'min': 0, 'max': 150, 'unit': 'mg/dL'},
            'HbA1c': {'min': 4.0, 'max': 5.6, 'unit': '%'},
            'ESR': {'min': 0, 'max': 20, 'unit': 'mm/hr'},
            'CRP': {'min': 0, 'max': 3.0, 'unit': 'mg/L'}
        }
        
        # Update existing tests with normal ranges
        print("🔄 Updating existing tests with normal ranges...")
        
        # Get all existing tests
        cursor.execute("SELECT id, name FROM test")
        existing_tests = cursor.fetchall()
        
        updated_count = 0
        for test_id, test_name in existing_tests:
            # Find matching range data (case-insensitive partial match)
            range_data = None
            for range_name, data in test_ranges.items():
                if range_name.lower() in test_name.lower() or test_name.lower() in range_name.lower():
                    range_data = data
                    break
            
            if range_data:
                cursor.execute("""
                    UPDATE test 
                    SET normal_range_min = ?, normal_range_max = ?, unit = ?
                    WHERE id = ?
                """, (range_data['min'], range_data['max'], range_data['unit'], test_id))
                updated_count += 1
                print(f"✅ Updated {test_name}: {range_data['min']}-{range_data['max']} {range_data['unit']}")
            else:
                # Set default values for unknown tests
                cursor.execute("""
                    UPDATE test 
                    SET normal_range_min = 0, normal_range_max = 100, unit = 'units'
                    WHERE id = ?
                """, (test_id,))
                print(f"⚠️ Set default range for {test_name}: 0-100 units")
        
        # Commit changes
        conn.commit()
        
        print(f"✅ Migration completed successfully!")
        print(f"📊 Updated {updated_count} tests with specific ranges")
        print(f"📊 Total tests processed: {len(existing_tests)}")
        
        # Verify the migration
        cursor.execute("SELECT name, normal_range_min, normal_range_max, unit FROM test LIMIT 5")
        sample_tests = cursor.fetchall()
        
        print("\n📋 Sample updated tests:")
        for test in sample_tests:
            print(f"   {test[0]}: {test[1]}-{test[2]} {test[3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def verify_migration():
    """Verify that the migration was successful"""
    db_path = 'data/pathology.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("PRAGMA table_info(test)")
        columns = cursor.fetchall()
        
        print("\n🔍 Current Test table structure:")
        for column in columns:
            print(f"   {column[1]} ({column[2]})")
        
        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM test WHERE normal_range_min IS NOT NULL AND normal_range_max IS NOT NULL")
        count = cursor.fetchone()[0]
        
        print(f"\n📊 Tests with normal ranges: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("🧪 Test Table Migration Script")
    print("=" * 50)
    
    # Run migration
    if migrate_test_table():
        print("\n" + "=" * 50)
        verify_migration()
        print("\n🎉 Migration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart your Flask application")
        print("   2. Visit /test-results-management to see the new interface")
        print("   3. Test the color-coded result validation")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
