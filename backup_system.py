#!/usr/bin/env python3
"""
Pathology Lab Database Backup System
Automatically creates backups of SQLite database
"""

import os
import shutil
import datetime
import sqlite3
import zipfile
from pathlib import Path

class DatabaseBackup:
    def __init__(self, db_path=None):
        """Initialize backup system"""
        if db_path is None:
            # Default to data directory
            self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            self.db_path = os.path.join(self.data_dir, 'pathology.db')
        else:
            self.db_path = db_path
            self.data_dir = os.path.dirname(db_path)
        
        # Create backup directory
        self.backup_dir = os.path.join(self.data_dir, 'backups')
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, backup_type='manual'):
        """Create a backup of the database"""
        try:
            if not os.path.exists(self.db_path):
                print(f"❌ Database file not found: {self.db_path}")
                return False
            
            # Generate backup filename with timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"pathology_backup_{backup_type}_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Create backup using SQLite backup API (safer than file copy)
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            
            # Perform backup
            source_conn.backup(backup_conn)
            
            # Close connections
            source_conn.close()
            backup_conn.close()
            
            # Create compressed backup
            zip_filename = f"pathology_backup_{backup_type}_{timestamp}.zip"
            zip_path = os.path.join(self.backup_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_path, backup_filename)
            
            # Remove uncompressed backup (keep only zip)
            os.remove(backup_path)
            
            # Get file size
            file_size = os.path.getsize(zip_path)
            size_mb = file_size / (1024 * 1024)
            
            print(f"✅ Backup created successfully!")
            print(f"📁 Location: {zip_path}")
            print(f"📊 Size: {size_mb:.2f} MB")
            print(f"🕒 Timestamp: {timestamp}")
            
            return zip_path
            
        except Exception as e:
            print(f"❌ Backup failed: {str(e)}")
            return False
    
    def restore_backup(self, backup_path):
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_path):
                print(f"❌ Backup file not found: {backup_path}")
                return False
            
            # Create backup of current database before restore
            current_backup = self.create_backup('pre_restore')
            if current_backup:
                print(f"📋 Current database backed up to: {current_backup}")
            
            # Extract backup if it's a zip file
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    # Extract to temporary location
                    temp_dir = os.path.join(self.backup_dir, 'temp_restore')
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                    
                    zipf.extractall(temp_dir)
                    
                    # Find the .db file
                    db_files = [f for f in os.listdir(temp_dir) if f.endswith('.db')]
                    if not db_files:
                        print("❌ No database file found in backup")
                        return False
                    
                    extracted_db = os.path.join(temp_dir, db_files[0])
            else:
                extracted_db = backup_path
            
            # Replace current database
            shutil.copy2(extracted_db, self.db_path)
            
            # Clean up temporary files
            if backup_path.endswith('.zip'):
                shutil.rmtree(temp_dir)
            
            print(f"✅ Database restored successfully from: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {str(e)}")
            return False
    
    def list_backups(self):
        """List all available backups"""
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('pathology_backup_') and file.endswith('.zip'):
                    file_path = os.path.join(self.backup_dir, file)
                    file_size = os.path.getsize(file_path)
                    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    backup_files.append({
                        'filename': file,
                        'path': file_path,
                        'size_mb': file_size / (1024 * 1024),
                        'created': file_time
                    })
            
            # Sort by creation time (newest first)
            backup_files.sort(key=lambda x: x['created'], reverse=True)
            
            print(f"\n📋 Available Backups ({len(backup_files)} found):")
            print("-" * 80)
            for i, backup in enumerate(backup_files, 1):
                print(f"{i:2d}. {backup['filename']}")
                print(f"    📁 Size: {backup['size_mb']:.2f} MB")
                print(f"    🕒 Created: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}")
                print()
            
            return backup_files
            
        except Exception as e:
            print(f"❌ Error listing backups: {str(e)}")
            return []
    
    def cleanup_old_backups(self, keep_days=30):
        """Remove backups older than specified days"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
            removed_count = 0
            
            for file in os.listdir(self.backup_dir):
                if file.startswith('pathology_backup_') and file.endswith('.zip'):
                    file_path = os.path.join(self.backup_dir, file)
                    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        removed_count += 1
                        print(f"🗑️ Removed old backup: {file}")
            
            print(f"✅ Cleanup complete. Removed {removed_count} old backups.")
            return removed_count
            
        except Exception as e:
            print(f"❌ Cleanup failed: {str(e)}")
            return 0
    
    def get_database_info(self):
        """Get information about the current database"""
        try:
            if not os.path.exists(self.db_path):
                print("❌ Database file not found")
                return None
            
            # Get file info
            file_size = os.path.getsize(self.db_path)
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(self.db_path))
            
            # Get database info
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            table_info = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                table_info[table_name] = count
            
            conn.close()
            
            print(f"\n📊 Database Information:")
            print("-" * 50)
            print(f"📁 Location: {self.db_path}")
            print(f"📊 Size: {file_size / (1024 * 1024):.2f} MB")
            print(f"🕒 Last Modified: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n📋 Tables and Record Counts:")
            for table, count in table_info.items():
                print(f"  • {table}: {count} records")
            
            return {
                'path': self.db_path,
                'size_mb': file_size / (1024 * 1024),
                'last_modified': file_time,
                'tables': table_info
            }
            
        except Exception as e:
            print(f"❌ Error getting database info: {str(e)}")
            return None

def main():
    """Command line interface for backup system"""
    import sys
    
    backup_system = DatabaseBackup()
    
    if len(sys.argv) < 2:
        print("🔧 Pathology Lab Database Backup System")
        print("\nUsage:")
        print("  python backup_system.py backup          - Create backup")
        print("  python backup_system.py list            - List backups")
        print("  python backup_system.py info            - Database info")
        print("  python backup_system.py cleanup         - Remove old backups")
        print("  python backup_system.py restore <file>  - Restore from backup")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'backup':
        backup_system.create_backup('manual')
    elif command == 'list':
        backup_system.list_backups()
    elif command == 'info':
        backup_system.get_database_info()
    elif command == 'cleanup':
        backup_system.cleanup_old_backups()
    elif command == 'restore' and len(sys.argv) > 2:
        backup_file = sys.argv[2]
        backup_system.restore_backup(backup_file)
    else:
        print("❌ Invalid command")

if __name__ == '__main__':
    main()
