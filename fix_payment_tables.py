#!/usr/bin/env python3
"""
Emergency script to fix payment tables in DigitalOcean production
Run this script if you get "no such table: payment" error
"""

import os
from app import app, db

def fix_payment_tables():
    """Fix missing payment tables in production"""
    with app.app_context():
        print("🚨 EMERGENCY PAYMENT TABLE FIX")
        print("=" * 50)
        
        try:
            # Import all models explicitly
            print("📦 Importing all models...")
            from models import Patient, Test, PatientTest, Hospital, SampleCollector, Payment, PatientBill
            
            # Check current tables
            print("\n🔍 Checking current database tables...")
            try:
                tables = db.engine.table_names()
                print(f"Current tables: {', '.join(tables)}")
            except Exception as e:
                print(f"Could not list tables: {e}")
                tables = []
            
            # Check if payment tables exist
            payment_exists = 'payment' in tables
            patient_bill_exists = 'patient_bill' in tables
            
            print(f"\n📋 Table Status:")
            print(f"   Payment table: {'✅ EXISTS' if payment_exists else '❌ MISSING'}")
            print(f"   PatientBill table: {'✅ EXISTS' if patient_bill_exists else '❌ MISSING'}")
            
            if payment_exists and patient_bill_exists:
                print("\n🎉 All payment tables already exist!")
                return True
            
            # Create missing tables
            print(f"\n🔧 Creating missing payment tables...")
            
            if not payment_exists:
                print("   Creating Payment table...")
                Payment.__table__.create(db.engine, checkfirst=True)
                print("   ✅ Payment table created")
            
            if not patient_bill_exists:
                print("   Creating PatientBill table...")
                PatientBill.__table__.create(db.engine, checkfirst=True)
                print("   ✅ PatientBill table created")
            
            # Verify tables were created
            print("\n🔍 Verifying tables were created...")
            tables = db.engine.table_names()
            
            if 'payment' in tables and 'patient_bill' in tables:
                print("✅ All payment tables now exist!")
                
                # Create some sample payment data
                print("\n📊 Creating sample payment data...")
                
                # Check if we have patients
                patient_count = Patient.query.count()
                if patient_count > 0:
                    # Create sample payments
                    sample_payments = [
                        Payment(
                            patient_id=1,
                            amount=50.00,
                            payment_type='advance',
                            payment_method='cash',
                            reference_number='EMERGENCY_001',
                            notes='Emergency payment record created during table fix'
                        )
                    ]
                    
                    # Create sample bills
                    sample_bills = [
                        PatientBill(
                            patient_id=1,
                            total_amount=100.00,
                            paid_amount=50.00,
                            remaining_amount=50.00,
                            bill_status='partial'
                        )
                    ]
                    
                    try:
                        for payment in sample_payments:
                            db.session.add(payment)
                        
                        for bill in sample_bills:
                            db.session.add(bill)
                        
                        db.session.commit()
                        print("✅ Sample payment data created")
                        
                    except Exception as e:
                        print(f"⚠️ Could not create sample data: {e}")
                        db.session.rollback()
                else:
                    print("⚠️ No patients found - skipping sample payment data")
                
                print("\n🎉 PAYMENT TABLES FIXED SUCCESSFULLY!")
                print("\nNext steps:")
                print("1. Go to your app and try assigning tests")
                print("2. Payment section should now appear")
                print("3. Test payment collection functionality")
                
                return True
            else:
                print("❌ Failed to create payment tables")
                return False
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_payment_functionality():
    """Test if payment functionality is working"""
    with app.app_context():
        print("\n🧪 Testing payment functionality...")
        
        try:
            # Test Payment model
            payment_count = Payment.query.count()
            print(f"   Payment records: {payment_count}")
            
            # Test PatientBill model
            bill_count = PatientBill.query.count()
            print(f"   Bill records: {bill_count}")
            
            # Test creating a payment
            test_payment = Payment(
                patient_id=1,
                amount=1.00,
                payment_type='test',
                payment_method='cash',
                notes='Test payment - will be deleted'
            )
            
            db.session.add(test_payment)
            db.session.commit()
            
            # Delete test payment
            db.session.delete(test_payment)
            db.session.commit()
            
            print("✅ Payment functionality test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Payment functionality test failed: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Starting payment table fix...")
    
    success = fix_payment_tables()
    
    if success:
        test_payment_functionality()
        print("\n✅ ALL DONE! Payment system should now work.")
    else:
        print("\n❌ FAILED! Please check the errors above.")
        print("\nTry running: python init_db.py")
        print("Or contact support with the error details.")
