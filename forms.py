from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, DateField, FloatField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length, Regexp, ValidationError
import re

class PatientForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50),
        Regexp(r'^[A-Za-z\s]+$', message="Name must contain only letters and spaces")
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=50),
        Regexp(r'^[A-Za-z\s]+$', message="Name must contain only letters and spaces")
    ])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=150)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                        validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=15),
        Regexp(r'^[\d\-\+\(\)\s]+$', message="Phone number must contain only digits, spaces, and common phone symbols")
    ])
    email = StringField('Email', validators=[Optional(), Email()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10, max=500)])
    medical_history = TextAreaField('Medical History', validators=[Optional(), Length(max=1000)])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=100)])
    hospital_name = SelectField('Hospital', choices=[], validators=[Optional()])
    collected_by = SelectField('Sample Collected By', choices=[], validators=[Optional()])
    submit = SubmitField('Register Patient')

    def validate_phone(self, phone):
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', phone.data)
        if len(digits_only) < 10:
            raise ValidationError('Phone number must contain at least 10 digits')

class TestForm(FlaskForm):
    name = StringField('Test Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    normal_range = StringField('Normal Range', validators=[Optional(), Length(max=100)])
    cost = FloatField('Cost', validators=[DataRequired(), NumberRange(min=0, max=10000)])
    category = SelectField('Category', choices=[
        ('', 'Select Category'),
        ('Blood', 'Blood Test'),
        ('Urine', 'Urine Test'),
        ('Stool', 'Stool Test'),
        ('Imaging', 'Imaging'),
        ('Biopsy', 'Biopsy'),
        ('Other', 'Other')
    ], validators=[Optional()])
    submit = SubmitField('Add Test')

    def validate_cost(self, cost):
        if cost.data is not None and cost.data < 0:
            raise ValidationError('Cost cannot be negative')
        if cost.data is not None and cost.data > 10000:
            raise ValidationError('Cost seems unusually high. Please verify.')

class PatientTestForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    test_id = SelectField('Test', coerce=int, validators=[DataRequired()])
    date_ordered = DateField('Date Ordered', validators=[Optional()])
    results = TextAreaField('Results', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    sample_collector = SelectField('Sample Collector', choices=[], validators=[Optional()])
    submit = SubmitField('Assign Test')

class MultipleTestAssignmentForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    date_ordered = DateField('Date Ordered', validators=[Optional()])
    sample_collector = SelectField('Sample Collector', choices=[], validators=[Optional()])
    notes = TextAreaField('General Notes', validators=[Optional()])
    submit = SubmitField('Assign All Tests')

class PaymentForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    amount = FloatField('Payment Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    payment_type = SelectField('Payment Type', choices=[
        ('advance', 'Advance Payment'),
        ('partial', 'Partial Payment'),
        ('full', 'Full Payment'),
        ('remaining', 'Remaining Payment')
    ], validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque')
    ], validators=[DataRequired()])
    reference_number = StringField('Reference Number', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Payment')

class BillForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    discount_percentage = FloatField('Discount %', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    discount_amount = FloatField('Discount Amount', validators=[Optional(), NumberRange(min=0)], default=0)
    due_date = DateField('Due Date', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Generate Bill')

class HospitalForm(FlaskForm):
    name = StringField('Hospital Name', validators=[DataRequired(), Length(min=2, max=100)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=500)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    email = StringField('Email', validators=[Optional(), Email()])
    submit = SubmitField('Add Hospital')

class SampleCollectorForm(FlaskForm):
    name = StringField('Collector Name', validators=[DataRequired(), Length(min=2, max=100)])
    employee_id = StringField('Employee ID', validators=[Optional(), Length(max=20)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    email = StringField('Email', validators=[Optional(), Email()])
    department = StringField('Department', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Add Sample Collector')

# Multi-step Patient Registration Forms
class PatientStep1Form(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50),
        Regexp(r'^[A-Za-z\s]+$', message="Name must contain only letters and spaces")
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=50),
        Regexp(r'^[A-Za-z\s]+$', message="Name must contain only letters and spaces")
    ])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=150)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                        validators=[DataRequired()])
    next_step = SubmitField('Next: Contact Information')

class PatientStep2Form(FlaskForm):
    phone = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=15),
        Regexp(r'^[\d\-\+\(\)\s]+$', message="Phone number must contain only digits, spaces, and common phone symbols")
    ])
    email = StringField('Email', validators=[Optional(), Email()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10, max=500)])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=100)])
    next_step = SubmitField('Next: Medical & Hospital Info')

    def validate_phone(self, phone):
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', phone.data)
        if len(digits_only) < 10:
            raise ValidationError('Phone number must contain at least 10 digits')

class PatientStep3Form(FlaskForm):
    medical_history = TextAreaField('Medical History', validators=[Optional(), Length(max=1000)])
    hospital_name = SelectField('Hospital', choices=[], validators=[Optional()])
    collected_by = SelectField('Sample Collected By', choices=[], validators=[Optional()])
    submit = SubmitField('Complete Registration')
