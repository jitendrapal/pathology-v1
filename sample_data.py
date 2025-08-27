"""
Sample data script for Pathology Lab Management System
Run this script to populate the database with sample data for testing
"""

from app import app, db
from models import Patient, Test, PatientTest, Hospital, SampleCollector, Payment, PatientBill
from datetime import datetime, timedelta

def create_sample_data():
    with app.app_context():
        # Clear existing data
        Payment.query.delete()
        PatientBill.query.delete()
        PatientTest.query.delete()
        Patient.query.delete()
        Test.query.delete()
        Hospital.query.delete()
        SampleCollector.query.delete()
        
        # Sample Tests
        tests = [
            Test(name="Complete Blood Count (CBC)", description="Measures different components of blood including red blood cells, white blood cells, and platelets", normal_range="RBC: 4.5-5.5 million/µL", cost=25.00, category="Blood"),
            Test(name="Basic Metabolic Panel", description="Tests glucose, electrolytes, and kidney function", normal_range="Glucose: 70-100 mg/dL", cost=30.00, category="Blood"),
            Test(name="Lipid Panel", description="Measures cholesterol and triglycerides", normal_range="Total Cholesterol: <200 mg/dL", cost=35.00, category="Blood"),
            Test(name="Urinalysis", description="Examines urine for various substances and cells", normal_range="Protein: Negative", cost=20.00, category="Urine"),
            Test(name="Thyroid Function Test", description="Measures TSH, T3, and T4 levels", normal_range="TSH: 0.4-4.0 mIU/L", cost=45.00, category="Blood"),
            Test(name="Liver Function Test", description="Tests liver enzymes and function", normal_range="ALT: 7-56 U/L", cost=40.00, category="Blood"),
            Test(name="Chest X-Ray", description="Imaging of chest and lungs", normal_range="No abnormalities", cost=75.00, category="Imaging"),
            Test(name="Stool Culture", description="Tests for bacteria and parasites in stool", normal_range="No pathogens", cost=50.00, category="Stool"),
        ]
        
        for test in tests:
            db.session.add(test)

        # Sample Hospitals
        hospitals = [
            Hospital(name="City General Hospital", address="123 Main St, Downtown, ST 12345", phone="555-0100", email="info@citygeneral.com"),
            Hospital(name="St. Mary's Medical Center", address="456 Oak Ave, Midtown, ST 12346", phone="555-0200", email="contact@stmarys.org"),
            Hospital(name="Regional Medical Center", address="789 Pine Rd, Uptown, ST 12347", phone="555-0300", email="admin@regional.med"),
            Hospital(name="Community Health Clinic", address="321 Elm St, Suburb, ST 12348", phone="555-0400", email="info@community.health"),
            Hospital(name="University Hospital", address="654 Campus Dr, University, ST 12349", phone="555-0500", email="contact@univ.hospital"),
        ]

        for hospital in hospitals:
            db.session.add(hospital)

        # Sample Collectors
        collectors = [
            SampleCollector(name="Alice Johnson", employee_id="SC001", phone="555-1001", email="alice.j@lab.com", department="Phlebotomy"),
            SampleCollector(name="Bob Smith", employee_id="SC002", phone="555-1002", email="bob.s@lab.com", department="Laboratory"),
            SampleCollector(name="Carol Davis", employee_id="SC003", phone="555-1003", email="carol.d@lab.com", department="Phlebotomy"),
            SampleCollector(name="David Wilson", employee_id="SC004", phone="555-1004", email="david.w@lab.com", department="Laboratory"),
            SampleCollector(name="Emma Brown", employee_id="SC005", phone="555-1005", email="emma.b@lab.com", department="Sample Processing"),
        ]

        for collector in collectors:
            db.session.add(collector)
        
        # Sample Patients
        patients = [
            Patient(first_name="John", last_name="Smith", age=45, gender="Male", phone="555-0101", email="john.smith@email.com", address="123 Main St, Anytown, ST 12345", medical_history="Hypertension, managed with medication", hospital_name="City General Hospital", collected_by="Alice Johnson"),
            Patient(first_name="Sarah", last_name="Johnson", age=32, gender="Female", phone="555-0102", email="sarah.j@email.com", address="456 Oak Ave, Somewhere, ST 12346", medical_history="No significant medical history", hospital_name="St. Mary's Medical Center", collected_by="Bob Smith"),
            Patient(first_name="Michael", last_name="Brown", age=58, gender="Male", phone="555-0103", email="m.brown@email.com", address="789 Pine Rd, Elsewhere, ST 12347", medical_history="Diabetes Type 2, family history of heart disease", hospital_name="Regional Medical Center", collected_by="Carol Davis"),
            Patient(first_name="Emily", last_name="Davis", age=28, gender="Female", phone="555-0104", email="emily.davis@email.com", address="321 Elm St, Nowhere, ST 12348", medical_history="Allergic to penicillin", hospital_name="Community Health Clinic", collected_by="David Wilson"),
            Patient(first_name="Robert", last_name="Wilson", age=67, gender="Male", phone="555-0105", email="r.wilson@email.com", address="654 Maple Dr, Anywhere, ST 12349", medical_history="High cholesterol, previous heart attack", hospital_name="University Hospital", collected_by="Emma Brown"),
        ]
        
        for patient in patients:
            db.session.add(patient)
        
        db.session.commit()
        
        # Sample Test Orders
        test_orders = [
            PatientTest(patient_id=1, test_id=1, date_ordered=datetime.now() - timedelta(days=2), status="Completed", results="RBC: 4.8 million/µL, WBC: 7,200/µL, Platelets: 250,000/µL - Normal", date_completed=datetime.now() - timedelta(days=1), sample_collector="Alice Johnson"),
            PatientTest(patient_id=1, test_id=2, date_ordered=datetime.now() - timedelta(days=2), status="Completed", results="Glucose: 95 mg/dL, Sodium: 140 mEq/L - Normal", date_completed=datetime.now() - timedelta(days=1), sample_collector="Bob Smith"),
            PatientTest(patient_id=2, test_id=4, date_ordered=datetime.now() - timedelta(days=1), status="Pending", sample_collector="Carol Davis"),
            PatientTest(patient_id=3, test_id=3, date_ordered=datetime.now() - timedelta(days=3), status="Completed", results="Total Cholesterol: 245 mg/dL - Elevated", date_completed=datetime.now() - timedelta(days=2), sample_collector="David Wilson"),
            PatientTest(patient_id=3, test_id=6, date_ordered=datetime.now() - timedelta(days=3), status="Completed", results="ALT: 42 U/L, AST: 38 U/L - Normal", date_completed=datetime.now() - timedelta(days=2), sample_collector="Emma Brown"),
            PatientTest(patient_id=4, test_id=1, date_ordered=datetime.now(), status="Pending", sample_collector="Alice Johnson"),
            PatientTest(patient_id=5, test_id=7, date_ordered=datetime.now() - timedelta(days=1), status="Pending", sample_collector="Carol Davis"),
        ]
        
        for order in test_orders:
            db.session.add(order)

        db.session.commit()

        # Sample Payments and Bills
        sample_payments = [
            Payment(patient_id=1, amount=30.00, payment_type='advance', payment_method='cash',
                   reference_number='CASH001', notes='Advance payment for CBC and Basic Metabolic Panel'),
            Payment(patient_id=2, amount=20.00, payment_type='full', payment_method='card',
                   reference_number='CARD002', notes='Full payment for Urinalysis'),
            Payment(patient_id=3, amount=50.00, payment_type='partial', payment_method='upi',
                   reference_number='UPI003', notes='Partial payment for Lipid Panel and Liver Function Test'),
            Payment(patient_id=5, amount=40.00, payment_type='advance', payment_method='bank_transfer',
                   reference_number='BANK005', notes='Advance payment for Chest X-Ray'),
        ]

        for payment in sample_payments:
            db.session.add(payment)

        # Sample Patient Bills
        sample_bills = [
            PatientBill(patient_id=1, total_amount=55.00, paid_amount=30.00, remaining_amount=25.00,
                       bill_status='partial', discount_amount=0.00),
            PatientBill(patient_id=2, total_amount=20.00, paid_amount=20.00, remaining_amount=0.00,
                       bill_status='paid', discount_amount=0.00),
            PatientBill(patient_id=3, total_amount=75.00, paid_amount=50.00, remaining_amount=25.00,
                       bill_status='partial', discount_amount=0.00),
            PatientBill(patient_id=4, total_amount=25.00, paid_amount=0.00, remaining_amount=25.00,
                       bill_status='pending', discount_amount=0.00),
            PatientBill(patient_id=5, total_amount=75.00, paid_amount=40.00, remaining_amount=35.00,
                       bill_status='partial', discount_amount=0.00),
        ]

        for bill in sample_bills:
            db.session.add(bill)

        db.session.commit()

        print("Sample data created successfully!")
        print(f"Created {len(hospitals)} hospitals")
        print(f"Created {len(collectors)} sample collectors")
        print(f"Created {len(tests)} tests")
        print(f"Created {len(patients)} patients")
        print(f"Created {len(test_orders)} test orders")
        print(f"Created {len(sample_payments)} payments")
        print(f"Created {len(sample_bills)} patient bills")

if __name__ == "__main__":
    create_sample_data()
