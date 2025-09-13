#!/usr/bin/env python3
"""
Database migration script to add unit column to test table
"""

import sqlite3
import os

def migrate_database():
    """Add unit column to test table"""
    db_path = 'data/pathology.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if unit column already exists
        cursor.execute("PRAGMA table_info(test)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'unit' in columns:
            print("✅ Unit column already exists!")
            conn.close()
            return True
        
        print("🔄 Adding unit column to test table...")
        
        # Add unit column
        cursor.execute("ALTER TABLE test ADD COLUMN unit VARCHAR(50)")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Successfully added unit column to test table!")
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
