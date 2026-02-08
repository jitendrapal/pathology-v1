"""
Script to update tests with unit and normal_range values
"""
from app import app, db
from models import Test

# Test data with units and normal ranges
test_data = {
    'Complete Blood Count (CBC)': {
        'unit': 'million/µL',
        'normal_range': '4.5-5.5'
    },
    'Thyroid Profile': {
        'unit': 'mIU/L',
        'normal_range': '0.4-4.0'
    },
    'Blood Sugar (Fasting)': {
        'unit': 'mg/dL',
        'normal_range': '70-100'
    },
    'Urine Analysis': {
        'unit': 'negative',
        'normal_range': 'Normal'
    },
    'Lipid Panel': {
        'unit': 'mg/dL',
        'normal_range': '<200'
    },
    'Liver Function Test': {
        'unit': 'U/L',
        'normal_range': '7-56'
    },
    'Hemoglobin': {
        'unit': 'g/dL',
        'normal_range': '12.0-16.0'
    },
    'Platelet Count': {
        'unit': 'thousand/µL',
        'normal_range': '150-450'
    },
    'Creatinine': {
        'unit': 'mg/dL',
        'normal_range': '0.6-1.2'
    },
    'HbA1c': {
        'unit': '%',
        'normal_range': '4.0-5.6'
    }
}

def update_tests():
    with app.app_context():
        print("🔄 Updating tests with unit and normal_range values...")
        
        # Get all tests
        tests = Test.query.all()
        updated_count = 0
        
        for test in tests:
            if test.name in test_data:
                data = test_data[test.name]
                test.unit = data['unit']
                test.normal_range = data['normal_range']
                updated_count += 1
                print(f"✅ Updated: {test.name} - Unit: {test.unit}, Range: {test.normal_range}")
            else:
                # Set default values for unknown tests
                if not test.unit:
                    test.unit = 'units'
                if not test.normal_range:
                    test.normal_range = 'Refer to lab'
                print(f"⚠️ Set default for: {test.name}")
        
        db.session.commit()
        print(f"\n✅ Successfully updated {updated_count} tests!")
        print(f"📊 Total tests in database: {len(tests)}")

if __name__ == '__main__':
    update_tests()

