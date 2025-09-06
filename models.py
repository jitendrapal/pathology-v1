from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10), nullable=False, default='Mr.')
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=False)
    medical_history = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    hospital_name = db.Column(db.String(100), nullable=True)
    collected_by = db.Column(db.String(100), nullable=True)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with PatientTest
    patient_tests = db.relationship('PatientTest', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        return f"{self.title} {self.first_name} {self.last_name}"

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    normal_range = db.Column(db.String(100), nullable=True)  # Keep for backward compatibility
    normal_range_min = db.Column(db.Float, nullable=True, default=0.0)  # Minimum normal value
    normal_range_max = db.Column(db.Float, nullable=True, default=100.0)  # Maximum normal value
    unit = db.Column(db.String(20), nullable=True, default='')  # Unit of measurement (mg/dL, %, etc.)
    cost = db.Column(db.Float, nullable=False, default=0.0)
    category = db.Column(db.String(50), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with PatientTest
    patient_tests = db.relationship('PatientTest', backref='test', lazy=True)
    
    def __repr__(self):
        return f'<Test {self.name}>'

class PatientTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime, nullable=True)
    results = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending')  # Pending, Completed, Cancelled
    notes = db.Column(db.Text, nullable=True)
    sample_collector = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<PatientTest {self.patient.full_name} - {self.test.name}>'

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Hospital {self.name}>'

class SampleCollector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    employee_id = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(50), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SampleCollector {self.name}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # 'advance', 'partial', 'full', 'remaining'
    payment_method = db.Column(db.String(20), nullable=False)  # 'cash', 'card', 'upi', 'bank_transfer'
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    reference_number = db.Column(db.String(50), nullable=True)  # Transaction ID, receipt number
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(100), nullable=True)  # Staff member who recorded payment

    # Relationship
    patient = db.relationship('Patient', backref=db.backref('payments', lazy=True))

    def __repr__(self):
        return f'<Payment {self.amount} for Patient {self.patient_id}>'

class PatientBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    paid_amount = db.Column(db.Float, nullable=False, default=0.0)
    remaining_amount = db.Column(db.Float, nullable=False, default=0.0)
    discount_amount = db.Column(db.Float, nullable=False, default=0.0)
    discount_percentage = db.Column(db.Float, nullable=False, default=0.0)
    bill_date = db.Column(db.DateTime, default=datetime.utcnow)
    bill_status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'partial', 'paid', 'overdue'
    due_date = db.Column(db.DateTime, nullable=True)

    # Relationship
    patient = db.relationship('Patient', backref=db.backref('bills', lazy=True))

    @property
    def final_amount(self):
        return self.total_amount - self.discount_amount

    @property
    def payment_status(self):
        if self.paid_amount >= self.final_amount:
            return 'Fully Paid'
        elif self.paid_amount > 0:
            return 'Partially Paid'
        else:
            return 'Unpaid'

    def __repr__(self):
        return f'<PatientBill {self.total_amount} for Patient {self.patient_id}>'
