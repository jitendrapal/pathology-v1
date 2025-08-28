#!/usr/bin/env python3
"""
Database migration script to add title column to patient table
"""

import sqlite3
import os

def migrate_database():
    """Add title column to patient table"""
    db_path = 'instance/pathology.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if title column already exists
        cursor.execute("PRAGMA table_info(patient)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'title' in columns:
            print("✅ Title column already exists!")
            conn.close()
            return True
        
        print("🔄 Adding title column to patient table...")
        
        # Add title column with default value
        cursor.execute("ALTER TABLE patient ADD COLUMN title VARCHAR(10) DEFAULT 'Mr.'")
        
        # Update existing records to have default title based on gender
        cursor.execute("""
            UPDATE patient 
            SET title = CASE 
                WHEN gender = 'Female' THEN 'Mrs.'
                WHEN gender = 'Male' THEN 'Mr.'
                ELSE 'Mr.'
            END
        """)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Successfully added title column to patient table!")
        print("📝 Updated existing records with default titles based on gender")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    success = migrate_database()
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
