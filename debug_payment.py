#!/usr/bin/env python3
"""
Debug script to check payment functionality in production
Run this script to verify payment tables and data exist
"""

from app import app, db
from models import Patient, Test, PatientTest, Payment, PatientBill

def debug_payment_system():
    """Debug payment system tables and data"""
    with app.app_context():
        print("=== PAYMENT SYSTEM DEBUG ===\n")
        
        try:
            # Check if tables exist
            print("1. Checking database tables...")
            
            # Check Payment table
            payment_count = Payment.query.count()
            print(f"   ✅ Payment table exists - {payment_count} records")
            
            # Check PatientBill table
            bill_count = PatientBill.query.count()
            print(f"   ✅ PatientBill table exists - {bill_count} records")
            
            # Check Patient table
            patient_count = Patient.query.count()
            print(f"   ✅ Patient table exists - {patient_count} records")
            
            # Check Test table
            test_count = Test.query.count()
            print(f"   ✅ Test table exists - {test_count} records")
            
            # Check PatientTest table
            patient_test_count = PatientTest.query.count()
            print(f"   ✅ PatientTest table exists - {patient_test_count} records")
            
        except Exception as e:
            print(f"   ❌ Error checking tables: {e}")
            return
        
        print("\n2. Checking payment data...")
        
        try:
            # Show sample payments
            payments = Payment.query.limit(5).all()
            if payments:
                print("   Sample payments:")
                for payment in payments:
                    print(f"   - Patient {payment.patient_id}: ${payment.amount} ({payment.payment_method})")
            else:
                print("   ⚠️  No payments found")
            
            # Show sample bills
            bills = PatientBill.query.limit(5).all()
            if bills:
                print("\n   Sample bills:")
                for bill in bills:
                    print(f"   - Patient {bill.patient_id}: Total ${bill.total_amount}, Paid ${bill.paid_amount}, Status: {bill.bill_status}")
            else:
                print("   ⚠️  No bills found")
                
        except Exception as e:
            print(f"   ❌ Error checking payment data: {e}")
        
        print("\n3. Testing payment functionality...")
        
        try:
            # Test creating a sample payment
            test_patient = Patient.query.first()
            if test_patient:
                print(f"   Testing with patient: {test_patient.full_name}")
                
                # Check if patient has tests
                patient_tests = PatientTest.query.filter_by(patient_id=test_patient.id).all()
                if patient_tests:
                    total_cost = sum([pt.test.cost for pt in patient_tests])
                    print(f"   Patient has {len(patient_tests)} tests, total cost: ${total_cost}")
                    
                    # Check patient bill
                    patient_bill = PatientBill.query.filter_by(patient_id=test_patient.id).first()
                    if patient_bill:
                        print(f"   Patient bill: ${patient_bill.total_amount} total, ${patient_bill.paid_amount} paid")
                        print(f"   Payment status: {patient_bill.payment_status}")
                    else:
                        print("   ⚠️  No bill found for this patient")
                else:
                    print("   ⚠️  Patient has no tests assigned")
            else:
                print("   ❌ No patients found in database")
                
        except Exception as e:
            print(f"   ❌ Error testing payment functionality: {e}")
        
        print("\n4. Checking form imports...")
        
        try:
            from forms import PaymentForm, BillForm
            print("   ✅ PaymentForm imported successfully")
            print("   ✅ BillForm imported successfully")
        except Exception as e:
            print(f"   ❌ Error importing forms: {e}")
        
        print("\n5. Checking routes...")
        
        try:
            from app import payments, add_payment, patient_billing
            print("   ✅ Payment routes imported successfully")
        except Exception as e:
            print(f"   ❌ Error importing payment routes: {e}")
        
        print("\n=== DEBUG COMPLETE ===")
        
        # Recommendations
        print("\n📋 RECOMMENDATIONS:")
        if payment_count == 0:
            print("   • Run 'python sample_data.py' to create sample payment data")
        if patient_count == 0:
            print("   • Run 'python sample_data.py' to create sample patients and tests")
        print("   • Check browser console for JavaScript errors")
        print("   • Verify payment section appears when tests are selected")
        print("   • Test payment collection in assign_multiple_tests page")

if __name__ == "__main__":
    debug_payment_system()
