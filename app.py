from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Configuration for production and development
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///pathology.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Handle PostgreSQL URL format for DigitalOcean
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

# Initialize database
from models import db, Patient, Test, PatientTest, Hospital, SampleCollector, Payment, PatientBill
db.init_app(app)

# Import forms
from forms import PatientForm, TestForm, PatientTestForm, HospitalForm, SampleCollectorForm, PatientStep1Form, PatientStep2Form, PatientStep3Form, MultipleTestAssignmentForm, PaymentForm, BillForm

@app.route('/')
def index():
    total_patients = Patient.query.count()
    total_tests = Test.query.count()
    pending_tests = PatientTest.query.filter_by(status='Pending').count()
    completed_tests = PatientTest.query.filter_by(status='Completed').count()
    recent_patients = Patient.query.order_by(Patient.date_registered.desc()).limit(5).all()

    # Use joinedload to avoid lazy loading issues
    from sqlalchemy.orm import joinedload
    recent_test_orders = PatientTest.query.options(
        joinedload(PatientTest.patient),
        joinedload(PatientTest.test)
    ).order_by(PatientTest.date_ordered.desc()).limit(5).all()

    return render_template('index.html',
                         total_patients=total_patients,
                         total_tests=total_tests,
                         pending_tests=pending_tests,
                         completed_tests=completed_tests,
                         recent_patients=recent_patients,
                         recent_test_orders=recent_test_orders)

# Patient Management Routes
@app.route('/patients')
def patients():
    search = request.args.get('search', '')
    if search:
        patients = Patient.query.filter(
            (Patient.first_name.contains(search)) |
            (Patient.last_name.contains(search)) |
            (Patient.phone.contains(search))
        ).all()
    else:
        patients = Patient.query.all()
    return render_template('patients.html', patients=patients, search=search)

@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    form = PatientForm()
    # Populate hospital dropdown
    hospitals = Hospital.query.all()
    form.hospital_name.choices = [('', 'Select Hospital')] + [(h.name, h.name) for h in hospitals]
    # Populate collected_by dropdown
    collectors = SampleCollector.query.all()
    form.collected_by.choices = [('', 'Select Collector')] + [(c.name, c.name) for c in collectors]

    if form.validate_on_submit():
        try:
            # Check for duplicate phone number
            existing_patient = Patient.query.filter_by(phone=form.phone.data).first()
            if existing_patient:
                flash('A patient with this phone number already exists.', 'error')
                return render_template('register_patient.html', form=form)

            patient = Patient(
                first_name=form.first_name.data.strip().title(),
                last_name=form.last_name.data.strip().title(),
                age=form.age.data,
                gender=form.gender.data,
                phone=form.phone.data.strip(),
                email=form.email.data.strip().lower() if form.email.data else None,
                address=form.address.data.strip(),
                medical_history=form.medical_history.data.strip() if form.medical_history.data else None,
                emergency_contact=form.emergency_contact.data.strip() if form.emergency_contact.data else None,
                hospital_name=form.hospital_name.data if form.hospital_name.data else None,
                collected_by=form.collected_by.data if form.collected_by.data else None
            )
            db.session.add(patient)
            db.session.commit()
            flash(f'Patient {patient.full_name} registered successfully!', 'success')
            return redirect(url_for('patients'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while registering the patient. Please try again.', 'error')
            app.logger.error(f'Error registering patient: {str(e)}')
    return render_template('register_patient.html', form=form)

@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    form = PatientForm(obj=patient)
    # Populate hospital dropdown
    hospitals = Hospital.query.all()
    form.hospital_name.choices = [('', 'Select Hospital')] + [(h.name, h.name) for h in hospitals]
    # Populate collected_by dropdown
    collectors = SampleCollector.query.all()
    form.collected_by.choices = [('', 'Select Collector')] + [(c.name, c.name) for c in collectors]

    if form.validate_on_submit():
        form.populate_obj(patient)
        db.session.commit()
        flash('Patient information updated successfully!', 'success')
        return redirect(url_for('patients'))
    return render_template('edit_patient.html', form=form, patient=patient)

@app.route('/patient_detail/<int:id>')
def patient_detail(id):
    patient = Patient.query.get_or_404(id)
    # Get all tests for this patient with eager loading
    from sqlalchemy.orm import joinedload
    patient_tests = PatientTest.query.options(
        joinedload(PatientTest.test)
    ).filter_by(patient_id=id).order_by(PatientTest.date_ordered.desc()).all()

    # Get all available tests for assignment
    all_tests = Test.query.all()

    # Get sample collectors for dropdown
    collectors = SampleCollector.query.all()

    return render_template('patient_detail.html',
                         patient=patient,
                         patient_tests=patient_tests,
                         all_tests=all_tests,
                         collectors=collectors)

@app.route('/update_patient_tests/<int:patient_id>', methods=['POST'])
def update_patient_tests(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    try:
        # Get all the test updates from the form
        test_ids = request.form.getlist('test_ids[]')
        statuses = request.form.getlist('statuses[]')
        results = request.form.getlist('results[]')
        notes = request.form.getlist('notes[]')

        # Update each test
        for i, test_id in enumerate(test_ids):
            if test_id:  # Only process if test_id exists
                patient_test = PatientTest.query.filter_by(
                    patient_id=patient_id,
                    id=int(test_id)
                ).first()

                if patient_test:
                    # Update status
                    if i < len(statuses):
                        old_status = patient_test.status
                        patient_test.status = statuses[i]

                        # Set completion date if status changed to Completed
                        if old_status != 'Completed' and statuses[i] == 'Completed':
                            patient_test.date_completed = datetime.now()

                    # Update results
                    if i < len(results):
                        patient_test.results = results[i] if results[i] else None

                    # Update notes
                    if i < len(notes):
                        patient_test.notes = notes[i] if notes[i] else None

        # Handle new test assignments
        new_test_ids = request.form.getlist('new_test_ids[]')
        if new_test_ids:
            sample_collector = request.form.get('sample_collector', '')
            for new_test_id in new_test_ids:
                if new_test_id:
                    new_patient_test = PatientTest(
                        patient_id=patient_id,
                        test_id=int(new_test_id),
                        date_ordered=datetime.now(),
                        status='Pending',
                        sample_collector=sample_collector if sample_collector else None
                    )
                    db.session.add(new_patient_test)

        db.session.commit()
        flash(f'Successfully updated tests for {patient.full_name}!', 'success')

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating tests. Please try again.', 'error')
        app.logger.error(f'Error updating patient tests: {str(e)}')

    return redirect(url_for('patient_detail', id=patient_id))

# Payment Management Routes
@app.route('/payments')
def payments():
    from sqlalchemy.orm import joinedload
    payments = Payment.query.options(
        joinedload(Payment.patient)
    ).order_by(Payment.payment_date.desc()).all()
    return render_template('payments.html', payments=payments)

@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    form = PaymentForm()
    form.patient_id.choices = [(p.id, p.full_name) for p in Patient.query.all()]

    if form.validate_on_submit():
        try:
            # Create payment record
            payment = Payment(
                patient_id=form.patient_id.data,
                amount=form.amount.data,
                payment_type=form.payment_type.data,
                payment_method=form.payment_method.data,
                reference_number=form.reference_number.data,
                notes=form.notes.data,
                created_by='Admin'  # In real app, use current user
            )
            db.session.add(payment)

            # Update or create patient bill
            patient_bill = PatientBill.query.filter_by(patient_id=form.patient_id.data).first()
            if not patient_bill:
                # Calculate total from assigned tests
                patient_tests = PatientTest.query.filter_by(patient_id=form.patient_id.data).all()
                total_amount = sum([pt.test.cost for pt in patient_tests])

                patient_bill = PatientBill(
                    patient_id=form.patient_id.data,
                    total_amount=total_amount,
                    paid_amount=form.amount.data,
                    remaining_amount=max(0, total_amount - form.amount.data)
                )
                db.session.add(patient_bill)
            else:
                patient_bill.paid_amount += form.amount.data
                patient_bill.remaining_amount = max(0, patient_bill.final_amount - patient_bill.paid_amount)

            # Update bill status
            if patient_bill.paid_amount >= patient_bill.final_amount:
                patient_bill.bill_status = 'paid'
            elif patient_bill.paid_amount > 0:
                patient_bill.bill_status = 'partial'
            else:
                patient_bill.bill_status = 'pending'

            db.session.commit()
            flash(f'Payment of ${form.amount.data:.2f} recorded successfully!', 'success')
            return redirect(url_for('payments'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while recording payment. Please try again.', 'error')
            app.logger.error(f'Error recording payment: {str(e)}')

    return render_template('add_payment.html', form=form)

@app.route('/patient_billing/<int:patient_id>')
def patient_billing(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Get or create patient bill
    patient_bill = PatientBill.query.filter_by(patient_id=patient_id).first()
    if not patient_bill:
        # Calculate total from assigned tests
        patient_tests = PatientTest.query.filter_by(patient_id=patient_id).all()
        total_amount = sum([pt.test.cost for pt in patient_tests])

        patient_bill = PatientBill(
            patient_id=patient_id,
            total_amount=total_amount,
            paid_amount=0,
            remaining_amount=total_amount
        )
        db.session.add(patient_bill)
        db.session.commit()

    # Get payment history
    payments = Payment.query.filter_by(patient_id=patient_id).order_by(Payment.payment_date.desc()).all()

    # Get test details
    from sqlalchemy.orm import joinedload
    patient_tests = PatientTest.query.options(
        joinedload(PatientTest.test)
    ).filter_by(patient_id=patient_id).all()

    return render_template('patient_billing.html',
                         patient=patient,
                         patient_bill=patient_bill,
                         payments=payments,
                         patient_tests=patient_tests)

@app.route('/update_bill/<int:patient_id>', methods=['POST'])
def update_bill(patient_id):
    patient_bill = PatientBill.query.filter_by(patient_id=patient_id).first_or_404()

    try:
        discount_percentage = float(request.form.get('discount_percentage', 0))
        discount_amount = float(request.form.get('discount_amount', 0))

        # Apply discount
        if discount_percentage > 0:
            patient_bill.discount_percentage = discount_percentage
            patient_bill.discount_amount = (patient_bill.total_amount * discount_percentage) / 100
        else:
            patient_bill.discount_amount = discount_amount
            patient_bill.discount_percentage = (discount_amount / patient_bill.total_amount) * 100 if patient_bill.total_amount > 0 else 0

        # Recalculate remaining amount
        patient_bill.remaining_amount = max(0, patient_bill.final_amount - patient_bill.paid_amount)

        # Update status
        if patient_bill.paid_amount >= patient_bill.final_amount:
            patient_bill.bill_status = 'paid'
        elif patient_bill.paid_amount > 0:
            patient_bill.bill_status = 'partial'

        db.session.commit()
        flash('Bill updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating bill. Please try again.', 'error')
        app.logger.error(f'Error updating bill: {str(e)}')

    return redirect(url_for('patient_billing', patient_id=patient_id))

@app.route('/collect_final_payment/<int:test_id>', methods=['POST'])
def collect_final_payment(test_id):
    """Collect final payment for a completed test"""
    try:
        patient_test = PatientTest.query.get_or_404(test_id)
        patient_id = patient_test.patient_id

        # Get payment details from form
        payment_amount = float(request.form.get('payment_amount', 0))
        payment_method = request.form.get('payment_method')
        reference_number = request.form.get('reference_number', '')

        # Get patient bill
        patient_bill = PatientBill.query.filter_by(patient_id=patient_id).first()
        if not patient_bill:
            flash('No billing information found for this patient.', 'error')
            return redirect(url_for('edit_patient_test', id=test_id))

        # Validate payment amount
        if payment_amount <= 0:
            flash('Payment amount must be greater than zero.', 'error')
            return redirect(url_for('edit_patient_test', id=test_id))

        if payment_amount > patient_bill.remaining_amount:
            flash('Payment amount cannot exceed remaining balance.', 'error')
            return redirect(url_for('edit_patient_test', id=test_id))

        # Create payment record
        payment = Payment(
            patient_id=patient_id,
            amount=payment_amount,
            payment_type='final' if payment_amount >= patient_bill.remaining_amount else 'partial',
            payment_method=payment_method,
            reference_number=reference_number,
            notes=f'Final payment for test: {patient_test.test.name}',
            created_by='Admin'  # In real app, use current user
        )
        db.session.add(payment)

        # Update patient bill
        patient_bill.paid_amount += payment_amount
        patient_bill.remaining_amount = max(0, patient_bill.final_amount - patient_bill.paid_amount)

        # Update bill status
        if patient_bill.remaining_amount <= 0:
            patient_bill.bill_status = 'paid'
            flash(f'Final payment of ${payment_amount:.2f} collected successfully! Test report is now ready for printing.', 'success')
        else:
            patient_bill.bill_status = 'partial'
            flash(f'Payment of ${payment_amount:.2f} collected successfully! Remaining balance: ${patient_bill.remaining_amount:.2f}', 'success')

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while processing payment. Please try again.', 'error')
        app.logger.error(f'Error collecting final payment: {str(e)}')

    return redirect(url_for('edit_patient_test', id=test_id))

@app.route('/print_test_report/<int:test_id>')
def print_test_report(test_id):
    """Print individual test report for a completed and paid test"""
    patient_test = PatientTest.query.get_or_404(test_id)

    # Check if test is completed
    if patient_test.status != 'Completed':
        flash('Test must be completed before printing report.', 'error')
        return redirect(url_for('edit_patient_test', id=test_id))

    # Check if payment is complete
    patient_bill = PatientBill.query.filter_by(patient_id=patient_test.patient_id).first()
    if patient_bill and patient_bill.remaining_amount > 0:
        flash('Payment must be completed before printing report.', 'error')
        return redirect(url_for('edit_patient_test', id=test_id))

    # Get all completed tests for this patient (for comprehensive report)
    from sqlalchemy.orm import joinedload
    all_completed_tests = PatientTest.query.options(
        joinedload(PatientTest.test)
    ).filter_by(
        patient_id=patient_test.patient_id,
        status='Completed'
    ).order_by(PatientTest.date_completed.desc()).all()

    # Get payment history
    payments = Payment.query.filter_by(patient_id=patient_test.patient_id).order_by(Payment.payment_date.desc()).all()

    return render_template('reports/test_report.html',
                         patient_test=patient_test,
                         patient=patient_test.patient,
                         all_completed_tests=all_completed_tests,
                         patient_bill=patient_bill,
                         payments=payments)

@app.route('/print_patient_report/<int:patient_id>')
def print_patient_report(patient_id):
    """Print comprehensive report for all completed tests of a patient"""
    patient = Patient.query.get_or_404(patient_id)

    # Get all completed tests for this patient
    from sqlalchemy.orm import joinedload
    completed_tests = PatientTest.query.options(
        joinedload(PatientTest.test)
    ).filter_by(
        patient_id=patient_id,
        status='Completed'
    ).order_by(PatientTest.date_completed.desc()).all()

    if not completed_tests:
        flash('No completed tests found for this patient.', 'error')
        return redirect(url_for('patient_detail', id=patient_id))

    # Check if all payments are complete
    patient_bill = PatientBill.query.filter_by(patient_id=patient_id).first()
    if patient_bill and patient_bill.remaining_amount > 0:
        flash('All payments must be completed before printing comprehensive report.', 'warning')
        return redirect(url_for('patient_billing', patient_id=patient_id))

    # Get payment history
    payments = Payment.query.filter_by(patient_id=patient_id).order_by(Payment.payment_date.desc()).all()

    return render_template('reports/patient_comprehensive_report.html',
                         patient=patient,
                         completed_tests=completed_tests,
                         patient_bill=patient_bill,
                         payments=payments)

# Bulk Update Routes
@app.route('/bulk_update_tests', methods=['GET'])
def bulk_update_tests():
    from sqlalchemy.orm import joinedload

    # Get filter parameters
    status_filter = request.args.get('status', '')
    patient_filter = request.args.get('patient', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # Build query
    query = PatientTest.query.options(
        joinedload(PatientTest.patient),
        joinedload(PatientTest.test)
    )

    # Apply filters
    if status_filter:
        query = query.filter(PatientTest.status == status_filter)
    if patient_filter:
        query = query.filter(PatientTest.patient_id == int(patient_filter))
    if date_from:
        from datetime import datetime
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        query = query.filter(PatientTest.date_ordered >= date_from_obj)
    if date_to:
        from datetime import datetime
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        query = query.filter(PatientTest.date_ordered <= date_to_obj)

    patient_tests = query.order_by(PatientTest.date_ordered.desc()).all()

    # Get all patients and collectors for dropdowns
    patients = Patient.query.all()
    collectors = SampleCollector.query.all()

    return render_template('bulk_update_tests.html',
                         patient_tests=patient_tests,
                         patients=patients,
                         collectors=collectors,
                         status_filter=status_filter,
                         patient_filter=patient_filter,
                         date_from=date_from,
                         date_to=date_to)

@app.route('/process_bulk_update', methods=['POST'])
def process_bulk_update():
    try:
        # Get selected test IDs
        selected_tests = request.form.getlist('selected_tests[]')
        if not selected_tests:
            flash('No tests selected for update.', 'error')
            return redirect(url_for('bulk_update_tests'))

        # Get bulk update values
        bulk_status = request.form.get('bulk_status')
        bulk_sample_collector = request.form.get('bulk_sample_collector')
        bulk_notes = request.form.get('bulk_notes')

        # Get individual values
        statuses = request.form.getlist('statuses[]')
        results = request.form.getlist('results[]')
        notes = request.form.getlist('notes[]')

        updated_count = 0

        # Update each selected test
        for i, test_id in enumerate(selected_tests):
            patient_test = PatientTest.query.get(int(test_id))
            if patient_test:
                # Update status (bulk or individual)
                if bulk_status:
                    old_status = patient_test.status
                    patient_test.status = bulk_status
                    if old_status != 'Completed' and bulk_status == 'Completed':
                        patient_test.date_completed = datetime.now()
                elif i < len(statuses) and statuses[i]:
                    old_status = patient_test.status
                    patient_test.status = statuses[i]
                    if old_status != 'Completed' and statuses[i] == 'Completed':
                        patient_test.date_completed = datetime.now()

                # Update sample collector
                if bulk_sample_collector:
                    patient_test.sample_collector = bulk_sample_collector

                # Update results
                if i < len(results) and results[i]:
                    patient_test.results = results[i]

                # Update notes (append bulk notes if provided)
                if i < len(notes) and notes[i]:
                    patient_test.notes = notes[i]
                if bulk_notes:
                    if patient_test.notes:
                        patient_test.notes += f"\n{bulk_notes}"
                    else:
                        patient_test.notes = bulk_notes

                updated_count += 1

        db.session.commit()
        flash(f'Successfully updated {updated_count} test orders!', 'success')

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating tests. Please try again.', 'error')
        app.logger.error(f'Error in bulk update: {str(e)}')

    return redirect(url_for('patient_tests'))

# Multi-step Patient Registration Routes
@app.route('/register_patient_step1', methods=['GET', 'POST'])
def register_patient_step1():
    form = PatientStep1Form()
    if form.validate_on_submit():
        # Store step 1 data in session
        from flask import session
        session['patient_step1'] = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'age': form.age.data,
            'gender': form.gender.data
        }
        return redirect(url_for('register_patient_step2'))
    return render_template('register_patient_step1.html', form=form)

@app.route('/register_patient_step2', methods=['GET', 'POST'])
def register_patient_step2():
    from flask import session
    if 'patient_step1' not in session:
        flash('Please start from the beginning.', 'error')
        return redirect(url_for('register_patient_step1'))

    form = PatientStep2Form()
    if form.validate_on_submit():
        # Store step 2 data in session
        session['patient_step2'] = {
            'phone': form.phone.data,
            'email': form.email.data,
            'address': form.address.data,
            'emergency_contact': form.emergency_contact.data
        }
        return redirect(url_for('register_patient_step3'))
    return render_template('register_patient_step2.html', form=form)

@app.route('/register_patient_step3', methods=['GET', 'POST'])
def register_patient_step3():
    from flask import session
    if 'patient_step1' not in session or 'patient_step2' not in session:
        flash('Please complete all previous steps.', 'error')
        return redirect(url_for('register_patient_step1'))

    form = PatientStep3Form()
    # Populate dropdowns
    hospitals = Hospital.query.all()
    form.hospital_name.choices = [('', 'Select Hospital')] + [(h.name, h.name) for h in hospitals]
    collectors = SampleCollector.query.all()
    form.collected_by.choices = [('', 'Select Collector')] + [(c.name, c.name) for c in collectors]

    if form.validate_on_submit():
        try:
            # Combine all data and create patient
            step1_data = session['patient_step1']
            step2_data = session['patient_step2']

            # Check for duplicate phone number
            existing_patient = Patient.query.filter_by(phone=step2_data['phone']).first()
            if existing_patient:
                flash('A patient with this phone number already exists.', 'error')
                return render_template('register_patient_step3.html', form=form)

            patient = Patient(
                first_name=step1_data['first_name'].strip().title(),
                last_name=step1_data['last_name'].strip().title(),
                age=step1_data['age'],
                gender=step1_data['gender'],
                phone=step2_data['phone'].strip(),
                email=step2_data['email'].strip().lower() if step2_data['email'] else None,
                address=step2_data['address'].strip(),
                emergency_contact=step2_data['emergency_contact'].strip() if step2_data['emergency_contact'] else None,
                medical_history=form.medical_history.data.strip() if form.medical_history.data else None,
                hospital_name=form.hospital_name.data if form.hospital_name.data else None,
                collected_by=form.collected_by.data if form.collected_by.data else None
            )
            db.session.add(patient)
            db.session.commit()

            # Clear session data
            session.pop('patient_step1', None)
            session.pop('patient_step2', None)

            flash(f'Patient {patient.full_name} registered successfully!', 'success')
            return redirect(url_for('patients'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while registering the patient. Please try again.', 'error')
            app.logger.error(f'Error registering patient: {str(e)}')

    return render_template('register_patient_step3.html', form=form)

# Test Management Routes
@app.route('/tests')
def tests():
    tests = Test.query.all()
    return render_template('tests.html', tests=tests)

@app.route('/add_test', methods=['GET', 'POST'])
def add_test():
    form = TestForm()
    if form.validate_on_submit():
        try:
            # Check for duplicate test name
            existing_test = Test.query.filter_by(name=form.name.data.strip()).first()
            if existing_test:
                flash('A test with this name already exists.', 'error')
                return render_template('add_test.html', form=form)

            test = Test(
                name=form.name.data.strip(),
                description=form.description.data.strip() if form.description.data else None,
                normal_range=form.normal_range.data.strip() if form.normal_range.data else None,
                cost=form.cost.data,
                category=form.category.data if form.category.data else None
            )
            db.session.add(test)
            db.session.commit()
            flash(f'Test "{test.name}" added successfully!', 'success')
            return redirect(url_for('tests'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the test. Please try again.', 'error')
            app.logger.error(f'Error adding test: {str(e)}')
    return render_template('add_test.html', form=form)

@app.route('/edit_test/<int:id>', methods=['GET', 'POST'])
def edit_test(id):
    test = Test.query.get_or_404(id)
    form = TestForm(obj=test)
    if form.validate_on_submit():
        form.populate_obj(test)
        db.session.commit()
        flash('Test updated successfully!', 'success')
        return redirect(url_for('tests'))
    return render_template('edit_test.html', form=form, test=test)

# Patient-Test Assignment Routes
@app.route('/patient_tests')
def patient_tests():
    from sqlalchemy.orm import joinedload

    # Get filter parameters
    status_filter = request.args.get('status', '')
    patient_filter = request.args.get('patient', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # Build query
    query = PatientTest.query.options(
        joinedload(PatientTest.patient),
        joinedload(PatientTest.test)
    )

    # Apply filters
    if status_filter:
        query = query.filter(PatientTest.status == status_filter)
    if patient_filter:
        query = query.filter(PatientTest.patient_id == int(patient_filter))
    if date_from:
        from datetime import datetime
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        query = query.filter(PatientTest.date_ordered >= date_from_obj)
    if date_to:
        from datetime import datetime
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        query = query.filter(PatientTest.date_ordered <= date_to_obj)

    patient_tests = query.order_by(PatientTest.date_ordered.desc()).all()

    # Get all patients for filter dropdown
    patients = Patient.query.all()

    return render_template('patient_tests.html',
                         patient_tests=patient_tests,
                         patients=patients,
                         status_filter=status_filter,
                         patient_filter=patient_filter,
                         date_from=date_from,
                         date_to=date_to)

@app.route('/assign_test', methods=['GET', 'POST'])
def assign_test():
    form = PatientTestForm()
    form.patient_id.choices = [(p.id, p.full_name) for p in Patient.query.all()]
    form.test_id.choices = [(t.id, t.name) for t in Test.query.all()]
    # Populate sample collector dropdown
    collectors = SampleCollector.query.all()
    form.sample_collector.choices = [('', 'Select Sample Collector')] + [(c.name, c.name) for c in collectors]

    if form.validate_on_submit():
        try:
            # Get test cost for billing
            test = Test.query.get(form.test_id.data)
            test_cost = test.cost

            patient_test = PatientTest(
                patient_id=form.patient_id.data,
                test_id=form.test_id.data,
                date_ordered=form.date_ordered.data or datetime.utcnow(),
                results=form.results.data,
                status=form.status.data,
                notes=form.notes.data,
                sample_collector=form.sample_collector.data if form.sample_collector.data else None
            )
            db.session.add(patient_test)

            # Handle payment collection if requested
            collect_payment = request.form.get('collect_payment')
            advance_amount = 0
            if collect_payment:
                advance_amount = float(request.form.get('advance_amount', 0))
                if advance_amount > 0:
                    # Create payment record
                    payment = Payment(
                        patient_id=form.patient_id.data,
                        amount=advance_amount,
                        payment_type='advance',
                        payment_method=request.form.get('payment_method', 'cash'),
                        reference_number=request.form.get('payment_reference'),
                        notes=request.form.get('payment_notes'),
                        created_by='Admin'  # In real app, use current user
                    )
                    db.session.add(payment)

            # Create or update patient bill
            patient_bill = PatientBill.query.filter_by(patient_id=form.patient_id.data).first()
            if not patient_bill:
                patient_bill = PatientBill(
                    patient_id=form.patient_id.data,
                    total_amount=test_cost,
                    paid_amount=advance_amount,
                    remaining_amount=max(0, test_cost - advance_amount),
                    bill_status='paid' if advance_amount >= test_cost else 'partial' if advance_amount > 0 else 'pending'
                )
                db.session.add(patient_bill)
            else:
                patient_bill.total_amount += test_cost
                patient_bill.paid_amount += advance_amount
                patient_bill.remaining_amount = max(0, patient_bill.final_amount - patient_bill.paid_amount)
                patient_bill.bill_status = 'paid' if patient_bill.paid_amount >= patient_bill.final_amount else 'partial' if patient_bill.paid_amount > 0 else 'pending'

            db.session.commit()

            # Success message with payment info
            if advance_amount > 0:
                flash(f'Test assigned successfully and collected ${advance_amount:.2f} advance payment! Remaining: ${max(0, test_cost - advance_amount):.2f}', 'success')
            else:
                flash(f'Test assigned successfully! Total cost: ${test_cost:.2f}', 'success')

            return redirect(url_for('patient_tests'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while assigning the test. Please try again.', 'error')
            app.logger.error(f'Error assigning test: {str(e)}')

    # Get all tests for JavaScript
    tests = Test.query.all()
    return render_template('assign_test.html', form=form, tests=tests)

@app.route('/edit_patient_test/<int:id>', methods=['GET', 'POST'])
def edit_patient_test(id):
    patient_test = PatientTest.query.get_or_404(id)
    form = PatientTestForm(obj=patient_test)
    form.patient_id.choices = [(p.id, p.full_name) for p in Patient.query.all()]
    form.test_id.choices = [(t.id, t.name) for t in Test.query.all()]
    # Populate sample collector dropdown
    collectors = SampleCollector.query.all()
    form.sample_collector.choices = [('', 'Select Sample Collector')] + [(c.name, c.name) for c in collectors]

    # Get patient billing information
    patient_bill = PatientBill.query.filter_by(patient_id=patient_test.patient_id).first()

    if form.validate_on_submit():
        form.populate_obj(patient_test)
        if form.status.data == 'Completed' and not patient_test.date_completed:
            patient_test.date_completed = datetime.utcnow()
        db.session.commit()
        flash('Test order updated successfully!', 'success')
        return redirect(url_for('patient_tests'))

    return render_template('edit_patient_test.html',
                         form=form,
                         patient_test=patient_test,
                         patient_bill=patient_bill)

# Multiple Test Assignment Routes
@app.route('/assign_multiple_tests', methods=['GET', 'POST'])
def assign_multiple_tests():
    form = MultipleTestAssignmentForm()
    form.patient_id.choices = [(p.id, p.full_name) for p in Patient.query.all()]
    # Populate sample collector dropdown
    collectors = SampleCollector.query.all()
    form.sample_collector.choices = [('', 'Select Sample Collector')] + [(c.name, c.name) for c in collectors]

    # Set default date to today
    if request.method == 'GET':
        form.date_ordered.data = datetime.now().date()

    if form.validate_on_submit():
        try:
            # Get the test IDs from the form data (will be sent via JavaScript)
            test_ids = request.form.getlist('test_ids[]')
            if not test_ids:
                flash('Please select at least one test.', 'error')
                return redirect(url_for('assign_multiple_tests'))

            # Create test assignments for each selected test and calculate total cost
            total_cost = 0
            for test_id in test_ids:
                test = Test.query.get(int(test_id))
                total_cost += test.cost

                patient_test = PatientTest(
                    patient_id=form.patient_id.data,
                    test_id=int(test_id),
                    date_ordered=form.date_ordered.data or datetime.utcnow(),
                    status='Pending',
                    notes=form.notes.data,
                    sample_collector=form.sample_collector.data if form.sample_collector.data else None
                )
                db.session.add(patient_test)

            # Handle payment collection if requested
            collect_payment = request.form.get('collect_payment')
            advance_amount = 0
            if collect_payment:
                advance_amount = float(request.form.get('advance_amount', 0))
                if advance_amount > 0:
                    # Create payment record
                    payment = Payment(
                        patient_id=form.patient_id.data,
                        amount=advance_amount,
                        payment_type='advance',
                        payment_method=request.form.get('payment_method', 'cash'),
                        reference_number=request.form.get('payment_reference'),
                        notes=request.form.get('payment_notes'),
                        created_by='Admin'  # In real app, use current user
                    )
                    db.session.add(payment)

            # Create or update patient bill
            patient_bill = PatientBill.query.filter_by(patient_id=form.patient_id.data).first()
            if not patient_bill:
                patient_bill = PatientBill(
                    patient_id=form.patient_id.data,
                    total_amount=total_cost,
                    paid_amount=advance_amount,
                    remaining_amount=max(0, total_cost - advance_amount),
                    bill_status='paid' if advance_amount >= total_cost else 'partial' if advance_amount > 0 else 'pending'
                )
                db.session.add(patient_bill)
            else:
                patient_bill.total_amount += total_cost
                patient_bill.paid_amount += advance_amount
                patient_bill.remaining_amount = max(0, patient_bill.final_amount - patient_bill.paid_amount)
                patient_bill.bill_status = 'paid' if patient_bill.paid_amount >= patient_bill.final_amount else 'partial' if patient_bill.paid_amount > 0 else 'pending'

            db.session.commit()

            # Success message with payment info
            if advance_amount > 0:
                flash(f'Successfully assigned {len(test_ids)} tests and collected ${advance_amount:.2f} advance payment! Remaining: ${max(0, total_cost - advance_amount):.2f}', 'success')
            else:
                flash(f'Successfully assigned {len(test_ids)} tests to patient! Total cost: ${total_cost:.2f}', 'success')

            return redirect(url_for('patient_tests'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while assigning tests. Please try again.', 'error')
            app.logger.error(f'Error assigning multiple tests: {str(e)}')

    # Get all tests for the grid
    tests = Test.query.all()
    return render_template('assign_multiple_tests.html', form=form, tests=tests)

# API route to get test details
@app.route('/api/test/<int:test_id>')
def get_test_details(test_id):
    test = Test.query.get_or_404(test_id)
    return jsonify({
        'id': test.id,
        'name': test.name,
        'description': test.description,
        'cost': test.cost,
        'category': test.category,
        'normal_range': test.normal_range
    })

# Report Generation Routes
@app.route('/reports/patient_tests')
def patient_tests_report():
    # Get same filters as main view
    status_filter = request.args.get('status', '')
    patient_filter = request.args.get('patient', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # Build query with same filters
    from sqlalchemy.orm import joinedload
    query = PatientTest.query.options(
        joinedload(PatientTest.patient),
        joinedload(PatientTest.test)
    )

    if status_filter:
        query = query.filter(PatientTest.status == status_filter)
    if patient_filter:
        query = query.filter(PatientTest.patient_id == int(patient_filter))
    if date_from:
        from datetime import datetime
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        query = query.filter(PatientTest.date_ordered >= date_from_obj)
    if date_to:
        from datetime import datetime
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        query = query.filter(PatientTest.date_ordered <= date_to_obj)

    patient_tests = query.order_by(PatientTest.date_ordered.desc()).all()

    # Calculate summary statistics
    total_tests = len(patient_tests)
    pending_tests = len([pt for pt in patient_tests if pt.status == 'Pending'])
    completed_tests = len([pt for pt in patient_tests if pt.status == 'Completed'])
    cancelled_tests = len([pt for pt in patient_tests if pt.status == 'Cancelled'])
    total_cost = sum([pt.test.cost for pt in patient_tests])

    return render_template('reports/patient_tests_report.html',
                         patient_tests=patient_tests,
                         total_tests=total_tests,
                         pending_tests=pending_tests,
                         completed_tests=completed_tests,
                         cancelled_tests=cancelled_tests,
                         total_cost=total_cost,
                         status_filter=status_filter,
                         patient_filter=patient_filter,
                         date_from=date_from,
                         date_to=date_to,
                         current_time=datetime.now())

@app.route('/reports/patient/<int:patient_id>')
def patient_report(patient_id):
    from sqlalchemy.orm import joinedload
    patient = Patient.query.get_or_404(patient_id)
    patient_tests = PatientTest.query.options(
        joinedload(PatientTest.test)
    ).filter_by(patient_id=patient_id).order_by(PatientTest.date_ordered.desc()).all()

    # Calculate patient statistics
    total_tests = len(patient_tests)
    pending_tests = len([pt for pt in patient_tests if pt.status == 'Pending'])
    completed_tests = len([pt for pt in patient_tests if pt.status == 'Completed'])
    total_cost = sum([pt.test.cost for pt in patient_tests])

    # Get billing information
    patient_bill = PatientBill.query.filter_by(patient_id=patient_id).first()
    paid_amount = patient_bill.paid_amount if patient_bill else 0
    remaining_amount = patient_bill.remaining_amount if patient_bill else total_cost

    return render_template('reports/patient_report.html',
                         patient=patient,
                         patient_tests=patient_tests,
                         total_tests=total_tests,
                         pending_tests=pending_tests,
                         completed_tests=completed_tests,
                         total_cost=total_cost,
                         paid_amount=paid_amount,
                         remaining_amount=remaining_amount,
                         current_time=datetime.now())

# Hospital Management Routes
@app.route('/hospitals')
def hospitals():
    hospitals = Hospital.query.all()
    return render_template('hospitals.html', hospitals=hospitals)

@app.route('/add_hospital', methods=['GET', 'POST'])
def add_hospital():
    form = HospitalForm()
    if form.validate_on_submit():
        try:
            # Check for duplicate hospital name
            existing_hospital = Hospital.query.filter_by(name=form.name.data.strip()).first()
            if existing_hospital:
                flash('A hospital with this name already exists.', 'error')
                return render_template('add_hospital.html', form=form)

            hospital = Hospital(
                name=form.name.data.strip(),
                address=form.address.data.strip() if form.address.data else None,
                phone=form.phone.data.strip() if form.phone.data else None,
                email=form.email.data.strip().lower() if form.email.data else None
            )
            db.session.add(hospital)
            db.session.commit()
            flash(f'Hospital "{hospital.name}" added successfully!', 'success')
            return redirect(url_for('hospitals'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the hospital. Please try again.', 'error')
            app.logger.error(f'Error adding hospital: {str(e)}')
    return render_template('add_hospital.html', form=form)

# Sample Collector Management Routes
@app.route('/sample_collectors')
def sample_collectors():
    collectors = SampleCollector.query.all()
    return render_template('sample_collectors.html', collectors=collectors)

@app.route('/add_sample_collector', methods=['GET', 'POST'])
def add_sample_collector():
    form = SampleCollectorForm()
    if form.validate_on_submit():
        try:
            # Check for duplicate collector name
            existing_collector = SampleCollector.query.filter_by(name=form.name.data.strip()).first()
            if existing_collector:
                flash('A sample collector with this name already exists.', 'error')
                return render_template('add_sample_collector.html', form=form)

            collector = SampleCollector(
                name=form.name.data.strip(),
                employee_id=form.employee_id.data.strip() if form.employee_id.data else None,
                phone=form.phone.data.strip() if form.phone.data else None,
                email=form.email.data.strip().lower() if form.email.data else None,
                department=form.department.data.strip() if form.department.data else None
            )
            db.session.add(collector)
            db.session.commit()
            flash(f'Sample collector "{collector.name}" added successfully!', 'success')
            return redirect(url_for('sample_collectors'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the sample collector. Please try again.', 'error')
            app.logger.error(f'Error adding sample collector: {str(e)}')
    return render_template('add_sample_collector.html', form=form)

def create_tables():
    """Create all database tables including Payment and PatientBill"""
    with app.app_context():
        try:
            # Import all models to ensure they're registered
            from models import Patient, Test, PatientTest, Hospital, SampleCollector, Payment, PatientBill

            # Create all tables
            db.create_all()
            print("✅ All database tables created successfully!")

            # Verify tables exist
            tables = db.engine.table_names()
            print(f"📋 Created tables: {', '.join(tables)}")

            # Check if Payment table exists
            if 'payment' in tables:
                print("✅ Payment table created")
            else:
                print("❌ Payment table missing")

            # Check if PatientBill table exists
            if 'patient_bill' in tables:
                print("✅ PatientBill table created")
            else:
                print("❌ PatientBill table missing")

        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            raise

if __name__ == '__main__':
    create_tables()

    # Get port from environment variable for deployment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'

    app.run(host='0.0.0.0', port=port, debug=debug)
