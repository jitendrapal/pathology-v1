# 🔧 Troubleshooting Guide for Pathology Lab Deployment

This guide helps you resolve common deployment issues on DigitalOcean and other platforms.

## 🚨 Common Deployment Issues & Solutions

### 1. **Email Validator Error** ✅ FIXED

**Error:**
```
Exception: Install 'email_validator' for email validation support.
```

**Solution:**
- ✅ **Fixed in latest commit** - Added `email-validator==2.0.0` to requirements.txt
- This dependency is required for WTForms email validation

### 2. **Database Connection Issues**

**Error:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solutions:**

#### A. Check Environment Variables
```bash
# In DigitalOcean App Platform Console
echo $DATABASE_URL
# Should show: postgresql://username:password@host:port/database
```

#### B. Verify Database Service
- Ensure PostgreSQL database is created and running
- Check database credentials in DigitalOcean dashboard
- Verify database and app are in same region

#### C. Initialize Database Tables
```bash
# Run in DigitalOcean Console
python init_db.py

# Or manually
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 3. **Port Binding Issues**

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
- ✅ **Fixed in latest commit** - App now uses `PORT` environment variable
- DigitalOcean automatically sets the PORT variable

### 4. **Secret Key Warnings**

**Error:**
```
WARNING: Do not use the development server in a production deployment.
```

**Solution:**
Set proper environment variables in DigitalOcean:

```bash
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
FLASK_ENV=production
```

### 5. **Static Files Not Loading**

**Error:**
CSS/JS files not loading, broken styling

**Solutions:**

#### A. Check Static File Configuration
```python
# In app.py (already configured)
app.static_folder = 'static'
app.static_url_path = '/static'
```

#### B. Use CDN for Bootstrap (Recommended)
```html
<!-- Already implemented in base.html -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
```

### 6. **Database Migration Issues**

**Error:**
```
Table 'patient' doesn't exist
```

**Solutions:**

#### A. Run Database Initialization
```bash
# Method 1: Use init script
python init_db.py

# Method 2: Manual initialization
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Method 3: Load sample data
python sample_data.py
```

#### B. Check Database Connection
```bash
# Test database connection
python -c "from app import app, db; app.app_context().push(); print('Database connected:', db.engine.url)"
```

### 7. **Memory/Resource Issues**

**Error:**
```
MemoryError: Unable to allocate memory
```

**Solutions:**

#### A. Upgrade App Plan
- Basic ($5/month) → Professional ($12/month)
- Increase memory from 512MB to 1GB

#### B. Optimize Database Queries
```python
# Use pagination for large datasets
patients = Patient.query.paginate(page=1, per_page=20)

# Use lazy loading
patient_tests = PatientTest.query.options(joinedload(PatientTest.patient)).all()
```

### 8. **Build Failures**

**Error:**
```
Build failed: requirements.txt not found
```

**Solutions:**

#### A. Check File Structure
```
pathology-v1/
├── app.py
├── requirements.txt  ← Must be in root
├── Procfile
├── runtime.txt
└── templates/
```

#### B. Verify requirements.txt Content
```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-WTF==1.1.1
WTForms==3.0.1
email-validator==2.0.0  ← Essential
gunicorn==21.2.0
psycopg2-binary==2.9.7
```

## 🔍 Debugging Steps

### 1. **Check Application Logs**

#### DigitalOcean App Platform:
1. Go to your app dashboard
2. Click "Runtime Logs" tab
3. Look for error messages

#### Common Log Locations:
```bash
# Application logs
tail -f /var/log/app.log

# System logs
journalctl -u your-app-name -f
```

### 2. **Test Database Connection**

```bash
# In DigitalOcean Console
python -c "
from app import app, db
with app.app_context():
    try:
        db.create_all()
        print('✅ Database connection successful')
    except Exception as e:
        print(f'❌ Database error: {e}')
"
```

### 3. **Verify Environment Variables**

```bash
# Check all environment variables
env | grep -E "(DATABASE_URL|SECRET_KEY|FLASK_ENV|PORT)"

# Test specific variables
echo "Database: $DATABASE_URL"
echo "Secret Key: ${SECRET_KEY:0:10}..." # Show first 10 chars only
echo "Environment: $FLASK_ENV"
echo "Port: $PORT"
```

### 4. **Test Application Routes**

```bash
# Test health endpoint
curl https://your-app-url.ondigitalocean.app/

# Test specific routes
curl https://your-app-url.ondigitalocean.app/patients
```

## 🛠️ Platform-Specific Solutions

### DigitalOcean App Platform

#### A. App Configuration
```yaml
# .do/app.yaml (optional)
name: pathology-lab
services:
- name: web
  source_dir: /
  github:
    repo: jitendrapal/pathology-v1
    branch: main
  run_command: gunicorn app:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: FLASK_ENV
    value: production
  - key: SECRET_KEY
    value: your-secret-key
databases:
- name: pathology-db
  engine: PG
  version: "13"
```

#### B. Database Setup
1. **Create Database**: Add PostgreSQL in app creation
2. **Get Connection String**: Copy from database settings
3. **Set Environment Variable**: `DATABASE_URL` is auto-set

#### C. Domain Configuration
1. **Custom Domain**: Add in "Settings" → "Domains"
2. **SSL Certificate**: Automatically provided
3. **DNS Configuration**: Point CNAME to app URL

### Heroku

#### A. Deployment Commands
```bash
# Login and create app
heroku login
heroku create pathology-lab-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Initialize database
heroku run python init_db.py
```

### Azure App Service

#### A. Configuration
```bash
# Set environment variables
az webapp config appsettings set --resource-group myResourceGroup --name pathology-lab --settings SECRET_KEY="your-secret-key" FLASK_ENV=production
```

## 📋 Pre-Deployment Checklist

### ✅ Code Preparation
- [ ] All dependencies in requirements.txt
- [ ] Environment variables configured
- [ ] Database models defined
- [ ] Static files properly referenced
- [ ] Debug mode disabled for production

### ✅ Database Setup
- [ ] Database service created
- [ ] Connection string obtained
- [ ] Tables will be created on first run
- [ ] Sample data script ready

### ✅ Security
- [ ] Strong SECRET_KEY set
- [ ] Database credentials secure
- [ ] No hardcoded passwords
- [ ] HTTPS enabled

### ✅ Testing
- [ ] Application runs locally
- [ ] Database operations work
- [ ] All routes accessible
- [ ] Forms submit correctly

## 🆘 Emergency Recovery

### If Deployment Completely Fails:

1. **Rollback to Previous Version**
```bash
# In DigitalOcean, go to "Deployments" and rollback
# Or redeploy from specific commit
```

2. **Start Fresh**
```bash
# Delete and recreate app
# Use known working configuration
```

3. **Local Testing**
```bash
# Test locally first
export DATABASE_URL="postgresql://localhost/test_db"
export SECRET_KEY="test-key"
export FLASK_ENV=production
python app.py
```

## 📞 Getting Help

### DigitalOcean Support
- **Community**: [DigitalOcean Community](https://www.digitalocean.com/community)
- **Documentation**: [App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- **Support Tickets**: Available for paid accounts

### Application Support
- **GitHub Issues**: [Create issue](https://github.com/jitendrapal/pathology-v1/issues)
- **Documentation**: Check README.md and DEPLOYMENT.md

---

**Remember**: Most deployment issues are related to missing dependencies or incorrect environment variables. Always check logs first! 🔍
