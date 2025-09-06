#!/usr/bin/env python3
"""
Migration script to add Doctor model and commission tracking
"""

import sqlite3
from datetime import datetime

def migrate_database():
    """Add Doctor table and update Patient table with referring_doctor_id"""
    
    conn = sqlite3.connect('data/pathology.db')
    cursor = conn.cursor()
    
    try:
        print("🔄 Starting Doctor model migration...")
        
        # Create Doctor table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                specialization VARCHAR(100),
                hospital_name VARCHAR(100),
                phone VARCHAR(15),
                email VARCHAR(100),
                commission_percentage FLOAT DEFAULT 0.0,
                commission_amount FLOAT DEFAULT 0.0,
                commission_type VARCHAR(20) NOT NULL DEFAULT 'percentage',
                address TEXT,
                license_number VARCHAR(50),
                date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        print("✅ Doctor table created successfully")
        
        # Create DoctorCommission table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_commission (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER NOT NULL,
                patient_id INTEGER NOT NULL,
                patient_test_id INTEGER NOT NULL,
                test_amount FLOAT NOT NULL,
                commission_amount FLOAT NOT NULL,
                commission_type VARCHAR(20) NOT NULL,
                commission_rate FLOAT,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
                date_paid DATETIME,
                payment_notes TEXT,
                FOREIGN KEY (doctor_id) REFERENCES doctor (id),
                FOREIGN KEY (patient_id) REFERENCES patient (id),
                FOREIGN KEY (patient_test_id) REFERENCES patient_test (id)
            )
        ''')
        print("✅ DoctorCommission table created successfully")
        
        # Check if Patient table exists, if not skip the column addition
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patient'")
        patient_table_exists = cursor.fetchone() is not None

        if patient_table_exists:
            # Add referring_doctor_id column to Patient table if it doesn't exist
            try:
                cursor.execute('ALTER TABLE patient ADD COLUMN referring_doctor_id INTEGER REFERENCES doctor(id)')
                print("✅ Added referring_doctor_id column to Patient table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️  referring_doctor_id column already exists in Patient table")
                else:
                    raise e
        else:
            print("ℹ️  Patient table doesn't exist yet - will be created by Flask app initialization")
        
        # Insert sample doctors with commission data
        sample_doctors = [
            ('Dr. Rajesh Kumar', 'Cardiologist', 'City Hospital', '9876543210', 'rajesh@cityhospital.com', 10.0, 0.0, 'percentage', 'City Hospital, Main Street', 'MED12345'),
            ('Dr. Priya Sharma', 'General Physician', 'General Hospital', '9876543211', 'priya@generalhospital.com', 8.0, 0.0, 'percentage', 'General Hospital, Park Road', 'MED12346'),
            ('Dr. Amit Singh', 'Orthopedic', 'Bone Care Center', '9876543212', 'amit@bonecare.com', 0.0, 50.0, 'fixed', 'Bone Care Center, Medical Complex', 'MED12347'),
            ('Dr. Sunita Patel', 'Gynecologist', 'Women\'s Hospital', '9876543213', 'sunita@womenshospital.com', 12.0, 0.0, 'percentage', 'Women\'s Hospital, Health Street', 'MED12348'),
            ('Dr. Vikram Gupta', 'Neurologist', 'Neuro Care Center', '9876543214', 'vikram@neurocare.com', 15.0, 0.0, 'percentage', 'Neuro Care Center, Brain Avenue', 'MED12349'),
            ('Dr. Kavita Reddy', 'Pathologist', 'Lab Diagnostics', '9876543215', 'kavita@labdiagnostics.com', 0.0, 75.0, 'fixed', 'Lab Diagnostics, Science Park', 'MED12350'),
            ('Dr. Ravi Mehta', 'Radiologist', 'Imaging Center', '9876543216', 'ravi@imagingcenter.com', 20.0, 0.0, 'percentage', 'Imaging Center, Tech Hub', 'MED12351'),
            ('Dr. Anjali Joshi', 'Dermatologist', 'Skin Care Clinic', '9876543217', 'anjali@skincare.com', 0.0, 40.0, 'fixed', 'Skin Care Clinic, Beauty Street', 'MED12352'),
            ('Dr. Manoj Agarwal', 'Endocrinologist', 'Diabetes Center', '9876543218', 'manoj@diabetescenter.com', 18.0, 0.0, 'percentage', 'Diabetes Center, Wellness Road', 'MED12353'),
            ('Dr. Deepika Nair', 'Pediatrician', 'Children\'s Hospital', '9876543219', 'deepika@childrenshospital.com', 10.0, 0.0, 'percentage', 'Children\'s Hospital, Kids Avenue', 'MED12354')
        ]
        
        for doctor_data in sample_doctors:
            cursor.execute('''
                INSERT OR IGNORE INTO doctor 
                (name, specialization, hospital_name, phone, email, commission_percentage, commission_amount, commission_type, address, license_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', doctor_data)
        
        print(f"✅ Added {len(sample_doctors)} sample doctors with commission data")
        
        # Update existing patients with referring doctors (only if patient table exists)
        if patient_table_exists:
            try:
                cursor.execute('''
                    UPDATE patient
                    SET referring_doctor_id = (
                        SELECT doctor.id
                        FROM doctor
                        WHERE doctor.name = patient.referring_doctor
                        LIMIT 1
                    )
                    WHERE patient.referring_doctor IS NOT NULL
                    AND patient.referring_doctor_id IS NULL
                ''')

                updated_patients = cursor.rowcount
                if updated_patients > 0:
                    print(f"✅ Updated {updated_patients} existing patients with doctor references")
            except sqlite3.OperationalError as e:
                print(f"ℹ️  Could not update patient references: {str(e)}")
        else:
            print("ℹ️  Skipping patient updates - table doesn't exist yet")
        
        conn.commit()
        print("🎉 Doctor migration completed successfully!")
        
        # Display summary
        cursor.execute('SELECT COUNT(*) FROM doctor')
        doctor_count = cursor.fetchone()[0]

        patients_with_doctors = 0
        if patient_table_exists:
            try:
                cursor.execute('SELECT COUNT(*) FROM patient WHERE referring_doctor_id IS NOT NULL')
                patients_with_doctors = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                patients_with_doctors = 0
        
        print(f"\n📊 Migration Summary:")
        print(f"   • Total doctors in system: {doctor_count}")
        print(f"   • Patients with assigned doctors: {patients_with_doctors}")
        print(f"   • Commission tracking: Enabled")
        print(f"   • Payment overview: Ready")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {str(e)}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
