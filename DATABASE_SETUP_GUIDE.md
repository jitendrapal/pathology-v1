# 🗄️ Database Setup Guide for Pathology Lab System

## 🎯 **Database Architecture Overview**

### **Development vs Production:**

| Environment | Database Type | Location | Installation Required |
|-------------|---------------|----------|----------------------|
| **Local Development** | SQLite | `pathology.db` file | ❌ No (built-in) |
| **Production (DigitalOcean)** | PostgreSQL | Managed Database Service | ❌ No (managed service) |

---

## 🔧 **How Database Creation Works**

### **❌ Previous Issue:**
- Database tables were NOT created automatically on deployment
- Required manual intervention after deployment
- Led to "no such table" errors

### **✅ New Solution:**
- **Automatic table creation** on app startup
- **Sample data loading** if database is empty
- **Startup script** runs before app starts
- **No manual intervention** required

---

## 🚀 **Automatic Database Initialization**

### **1. App Startup Initialization:**
```python
# In app.py - runs when app starts
with app.app_context():
    init_database()
```

### **2. Deployment Startup Script:**
```bash
# In Procfile
release: python startup.py  # Runs before app starts
web: gunicorn app:app       # Starts the app
```

### **3. Manual Initialization (if needed):**
```bash
# Emergency database setup
python startup.py
python fix_payment_tables.py
python sample_data.py
```

---

## 📋 **Database Tables Created Automatically**

### **Core Tables:**
1. **`patient`** - Patient information and demographics
2. **`test`** - Available tests and their details
3. **`patient_test`** - Test orders and results
4. **`hospital`** - Hospital information
5. **`sample_collector`** - Lab staff information

### **Payment Tables:**
6. **`payment`** - Payment records and transactions
7. **`patient_bill`** - Billing summaries and balances

### **Table Relationships:**
```
Patient (1) → (Many) PatientTest → (1) Test
Patient (1) → (Many) Payment
Patient (1) → (1) PatientBill
```

---

## 🔍 **Database Verification**

### **Check Tables Exist:**
```bash
# In DigitalOcean Console
python -c "
from app import app, db
with app.app_context():
    tables = db.engine.table_names()
    print('Tables:', tables)
"
```

### **Check Data Exists:**
```bash
# Check sample data
python debug_payment.py
```

### **Expected Output:**
```
✅ Patient table exists - 5 records
✅ Test table exists - 10 records
✅ Payment table exists - 4 records
✅ PatientBill table exists - 5 records
```

---

## 🛠️ **Deployment Process**

### **DigitalOcean App Platform:**

#### **Step 1: Automatic Deployment**
- Code pushes to GitHub
- DigitalOcean automatically deploys
- `startup.py` runs first (creates tables)
- App starts with database ready

#### **Step 2: Verification**
```bash
# In DigitalOcean Console
python startup.py
# Should show: ✅ Database initialization completed successfully!
```

#### **Step 3: Test Application**
- Visit your app URL
- Navigate to "Patients" - should work
- Try "Assign Tests" - should work
- Check "Payments" - should work

---

## 🔧 **Database Configuration**

### **Environment Variables:**
```bash
# Production (DigitalOcean sets automatically)
DATABASE_URL=postgresql://username:password@host:port/database

# Development (uses SQLite by default)
DATABASE_URL=sqlite:///pathology.db
```

### **Connection Handling:**
```python
# Automatic PostgreSQL URL format handling
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
```

---

## 📊 **Sample Data Loading**

### **Automatic Loading:**
- Runs if database is empty (0 patients, 0 tests)
- Creates realistic sample data for testing
- Includes patients, tests, orders, payments, bills

### **Sample Data Includes:**
- **5 Patients** with realistic information
- **10 Tests** with costs and descriptions
- **8 Test Orders** with various statuses
- **4 Payment Records** with different methods
- **5 Patient Bills** with payment tracking

### **Manual Sample Data:**
```bash
# Force reload sample data
python sample_data.py
```

---

## 🚨 **Troubleshooting Database Issues**

### **Issue 1: "No such table" errors**
```bash
# Solution
python fix_payment_tables.py
```

### **Issue 2: Empty database**
```bash
# Solution
python startup.py
```

### **Issue 3: Connection errors**
```bash
# Check database URL
echo $DATABASE_URL

# Test connection
python -c "from app import app, db; app.app_context().push(); print('Connected:', db.engine.url)"
```

### **Issue 4: Missing payment tables**
```bash
# Emergency fix
python -c "
from app import app, db
from models import Payment, PatientBill
with app.app_context():
    Payment.__table__.create(db.engine, checkfirst=True)
    PatientBill.__table__.create(db.engine, checkfirst=True)
    print('Payment tables created')
"
```

---

## 🔄 **Database Reset (if needed)**

### **Complete Reset:**
```bash
# WARNING: This deletes all data
python -c "
from app import app, db
with app.app_context():
    db.drop_all()
    db.create_all()
    print('Database reset complete')
"

# Reload sample data
python sample_data.py
```

### **Partial Reset (keep structure):**
```bash
# Clear data but keep tables
python -c "
from app import app, db
from models import *
with app.app_context():
    PatientTest.query.delete()
    Payment.query.delete()
    PatientBill.query.delete()
    Patient.query.delete()
    Test.query.delete()
    db.session.commit()
    print('Data cleared')
"
```

---

## 📈 **Database Monitoring**

### **Check Database Health:**
```bash
# Table counts
python -c "
from app import app, db
from models import *
with app.app_context():
    print(f'Patients: {Patient.query.count()}')
    print(f'Tests: {Test.query.count()}')
    print(f'Orders: {PatientTest.query.count()}')
    print(f'Payments: {Payment.query.count()}')
    print(f'Bills: {PatientBill.query.count()}')
"
```

### **Check Payment System:**
```bash
python debug_payment.py
```

---

## ✅ **Success Indicators**

### **Database Working Correctly:**
- ✅ All 7 tables created
- ✅ Sample data loaded
- ✅ No "table not found" errors
- ✅ Payment system functional
- ✅ Test assignment works
- ✅ Report generation works

### **Application Ready:**
- ✅ Homepage loads
- ✅ Patient registration works
- ✅ Test assignment with payment works
- ✅ Test result entry works
- ✅ Report printing works

---

## 🎯 **Summary**

**Your database is now:**
- ✅ **Automatically created** on deployment
- ✅ **Self-initializing** with sample data
- ✅ **Production-ready** with PostgreSQL
- ✅ **Development-friendly** with SQLite
- ✅ **Fully integrated** with payment system

**No manual database setup required!** The system handles everything automatically. 🚀
