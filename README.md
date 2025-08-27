# Pathology Lab Management System

A comprehensive web application for managing pathology laboratory operations, including patient registration, test management, and test result tracking.

## Features

### 1. Patient Management
- **Patient Registration**: Register new patients with comprehensive details
  - Personal information (name, age, gender, contact details)
  - Address and emergency contact information
  - Medical history tracking
- **Patient Search**: Search patients by name or phone number
- **Patient Editing**: Update patient information as needed
- **Patient Details View**: View complete patient information in modal dialogs

### 2. Test Catalog Management
- **Add New Tests**: Pathology staff can add new test types to the catalog
  - Test name and description
  - Test categories (Blood, Urine, Stool, Imaging, Biopsy, Other)
  - Normal ranges and cost information
- **Edit Tests**: Update test information including pricing and normal ranges
- **Test Categories**: Organize tests by medical categories

### 3. Test Order Management
- **Assign Tests to Patients**: Create test orders linking patients to specific tests
- **Track Test Status**: Monitor test progress (Pending, Completed, Cancelled)
- **Result Management**: Enter and update test results
- **Order History**: View complete history of all test orders

### 4. Dashboard & Analytics
- **Statistics Overview**: View total patients, available tests, pending and completed tests
- **Recent Activity**: Track recent patient registrations and test orders
- **Quick Actions**: Fast access to common operations

## Technology Stack

- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: SQLite (easily portable, suitable for small to medium labs)
- **Frontend**: HTML5, Bootstrap 5, Font Awesome icons
- **Forms**: Flask-WTF with comprehensive validation
- **Responsive Design**: Mobile-friendly interface

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

#### Installing Python (if not already installed)
1. **Windows**: Download Python from [python.org](https://www.python.org/downloads/) and install it
   - Make sure to check "Add Python to PATH" during installation
2. **Alternative**: Use the Microsoft Store to install Python
3. **Verify installation**: Open Command Prompt and run `python --version`

### Step 1: Clone or Download
Download the pathology application files to your desired directory.

### Step 2: Install Dependencies
Open Command Prompt in the application directory and run:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
**Option A - Using the batch file (Windows):**
```bash
run.bat
```

**Option B - Manual start:**
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 4: Access the Application
Open your web browser and navigate to `http://localhost:5000`

### Step 5: Load Sample Data (Optional)
To get started quickly with sample data:
```bash
python sample_data.py
```
This will create sample patients, tests, and test orders for demonstration purposes.

## Database Setup

The application automatically creates the SQLite database (`pathology.db`) on first run. No manual database setup is required.

## Usage Guide

### Getting Started
1. **Add Test Types**: Start by adding the tests your lab offers
   - Navigate to "Tests" → "Add New Test"
   - Enter test details including name, category, cost, and normal ranges

2. **Register Patients**: Add patients to the system
   - Navigate to "Patients" → "Register New Patient"
   - Fill in patient information including contact details and medical history

3. **Assign Tests**: Create test orders for patients
   - Navigate to "Test Orders" → "Assign Test to Patient"
   - Select patient and test, set status and add any notes

4. **Manage Results**: Update test orders with results
   - Navigate to "Test Orders" and click "Edit" on any order
   - Enter results and update status to "Completed"

### Key Workflows

#### Patient Registration Workflow
1. Click "Register New Patient" from dashboard or patients page
2. Fill in required fields (marked with *)
3. Add optional medical history and emergency contact
4. Submit to create patient record

#### Test Management Workflow
1. Add tests to catalog via "Add New Test"
2. Assign tests to patients via "Assign Test to Patient"
3. Update test status and results as tests are completed
4. View test history and patient results

## Data Validation

The application includes comprehensive validation:
- **Patient Data**: Name validation, phone number format checking, email validation
- **Test Data**: Unique test names, cost validation, category selection
- **Form Security**: CSRF protection on all forms
- **Error Handling**: Graceful error handling with user-friendly messages

## File Structure

```
pathology/
├── app.py                 # Main application file
├── models.py              # Database models
├── forms.py               # Form definitions and validation
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── pathology.db          # SQLite database (created automatically)
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Dashboard
    ├── patients.html     # Patient list
    ├── register_patient.html
    ├── edit_patient.html
    ├── tests.html        # Test catalog
    ├── add_test.html
    ├── edit_test.html
    ├── patient_tests.html # Test orders
    ├── assign_test.html
    └── edit_patient_test.html
```

## Customization

### Adding New Test Categories
Edit the `category` choices in `forms.py` in the `TestForm` class:
```python
category = SelectField('Category', choices=[
    ('Blood', 'Blood Test'),
    ('YourCategory', 'Your Category Name'),
    # Add more categories as needed
])
```

### Modifying Patient Fields
Add new fields to the `Patient` model in `models.py` and corresponding form fields in `forms.py`.

## Security Features

- CSRF protection on all forms
- Input validation and sanitization
- SQL injection prevention through SQLAlchemy ORM
- XSS protection through template escaping

## Support & Maintenance

### Backup
Regularly backup the `pathology.db` file to preserve your data.

### Updates
To update the application:
1. Backup your database
2. Replace application files
3. Run `pip install -r requirements.txt` to update dependencies
4. Restart the application

## Troubleshooting

### Common Issues
1. **Port already in use**: Change the port in `app.py` by modifying `app.run(debug=True, port=5001)`
2. **Database errors**: Delete `pathology.db` to reset the database (will lose all data)
3. **Permission errors**: Ensure the application directory is writable

### Getting Help
Check the console output for error messages. Most issues are related to missing dependencies or file permissions.

## License

This pathology lab management system is provided as-is for educational and commercial use.
