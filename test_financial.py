from app import app
from models import Patient, PatientTest, PatientBill, Doctor, Payment

with app.app_context():
    print('Testing financial overview logic...')
    patients = Patient.query.all()
    print(f'Found {len(patients)} patients')
    
    doctor_commission_summary = {}
    
    for patient in patients[:1]:
        print(f'\nPatient: {patient.full_name}')
        patient_tests = PatientTest.query.filter_by(patient_id=patient.id).all()
        print(f'  Tests: {len(patient_tests)}')
        
        patient_bill = PatientBill.query.filter_by(patient_id=patient.id).first()
        print(f'  Bill: {patient_bill}')
        
        if patient.referring_doctor_id:
            doctor = Doctor.query.get(patient.referring_doctor_id)
            print(f'  Doctor: {doctor.name if doctor else None}')
            
            if doctor and doctor.is_active:
                for pt in patient_tests:
                    print(f'    Test: {pt.test.name}, Cost: {pt.test.cost}')
                    commission = doctor.calculate_commission(pt.test.cost)
                    print(f'    Commission: {commission}')
    
    print('\nTest completed successfully!')

