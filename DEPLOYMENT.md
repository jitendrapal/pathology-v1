# 🚀 Deployment Guide for Pathology Lab Management System

This guide provides step-by-step instructions for deploying the Pathology Lab Management System to various platforms.

## 🌊 DigitalOcean App Platform (Recommended)

### Prerequisites
- DigitalOcean account
- GitHub repository (already set up)

### Steps

1. **Login to DigitalOcean**
   - Go to [DigitalOcean](https://www.digitalocean.com/)
   - Sign in to your account

2. **Create New App**
   - Click "Create" → "Apps"
   - Choose "GitHub" as source
   - Select repository: `jitendrapal/pathology-v1`
   - Branch: `main`

3. **Configure App Settings**
   ```yaml
   Name: pathology-lab
   Region: Choose closest to your location
   Plan: Basic ($5/month)
   ```

4. **Add Database**
   - Click "Add Database"
   - Choose "PostgreSQL"
   - Plan: Basic ($15/month)
   - Name: `pathology-db`

5. **Set Environment Variables**
   ```bash
   SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
   DATABASE_URL=${db.DATABASE_URL}
   FLASK_ENV=production
   ```

6. **Deploy**
   - Click "Create Resources"
   - Wait for deployment (5-10 minutes)

7. **Initialize Database**
   - Go to Console tab in your app
   - Run:
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   python sample_data.py
   ```

8. **Access Your App**
   - Your app will be available at: `https://pathology-lab-xxxxx.ondigitalocean.app`

**Total Cost: ~$20/month**

---

## 🔷 Azure App Service

### Prerequisites
- Azure account with $200 free credits
- GitHub repository

### Steps

1. **Create Resource Group**
   ```bash
   az group create --name pathology-rg --location "East US"
   ```

2. **Create App Service Plan**
   ```bash
   az appservice plan create --name pathology-plan --resource-group pathology-rg --sku B1 --is-linux
   ```

3. **Create Web App**
   ```bash
   az webapp create --resource-group pathology-rg --plan pathology-plan --name pathology-lab-app --runtime "PYTHON|3.11" --deployment-source-url https://github.com/jitendrapal/pathology-v1
   ```

4. **Create Database**
   ```bash
   az sql server create --name pathology-server --resource-group pathology-rg --location "East US" --admin-user sqladmin --admin-password YourPassword123!
   az sql db create --resource-group pathology-rg --server pathology-server --name pathology-db --service-objective Basic
   ```

5. **Configure App Settings**
   ```bash
   az webapp config appsettings set --resource-group pathology-rg --name pathology-lab-app --settings SECRET_KEY="your-secret-key" DATABASE_URL="postgresql://sqladmin:YourPassword123!@pathology-server.database.windows.net/pathology-db"
   ```

**Total Cost: ~$15/month**

---

## 🟠 AWS Elastic Beanstalk

### Prerequisites
- AWS account
- AWS CLI installed

### Steps

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB Application**
   ```bash
   eb init pathology-lab --platform python-3.11 --region us-east-1
   ```

3. **Create Environment**
   ```bash
   eb create pathology-production --database.engine postgres --database.username pathology --database.password YourPassword123
   ```

4. **Set Environment Variables**
   ```bash
   eb setenv SECRET_KEY="your-secret-key" FLASK_ENV=production
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

**Total Cost: ~$25/month**

---

## 🖥️ VPS Deployment (Ubuntu)

### Prerequisites
- VPS with Ubuntu 20.04+ (DigitalOcean Droplet, Linode, etc.)
- Domain name (optional)

### Steps

1. **Connect to Server**
   ```bash
   ssh root@your-server-ip
   ```

2. **Update System**
   ```bash
   apt update && apt upgrade -y
   ```

3. **Install Dependencies**
   ```bash
   apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib git -y
   ```

4. **Create User**
   ```bash
   adduser pathology
   usermod -aG sudo pathology
   su - pathology
   ```

5. **Clone Repository**
   ```bash
   git clone https://github.com/jitendrapal/pathology-v1.git
   cd pathology-v1
   ```

6. **Setup Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

7. **Setup PostgreSQL**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE pathology_db;
   CREATE USER pathology_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE pathology_db TO pathology_user;
   \q
   ```

8. **Configure Application**
   ```bash
   # Update app.py with production database URL
   export DATABASE_URL="postgresql://pathology_user:secure_password@localhost/pathology_db"
   export SECRET_KEY="your-super-secret-key"
   ```

9. **Initialize Database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   python sample_data.py
   ```

10. **Setup Gunicorn Service**
    ```bash
    sudo nano /etc/systemd/system/pathology.service
    ```
    
    Add:
    ```ini
    [Unit]
    Description=Gunicorn instance to serve Pathology Lab
    After=network.target

    [Service]
    User=pathology
    Group=www-data
    WorkingDirectory=/home/pathology/pathology-v1
    Environment="PATH=/home/pathology/pathology-v1/venv/bin"
    ExecStart=/home/pathology/pathology-v1/venv/bin/gunicorn --workers 3 --bind unix:pathology.sock -m 007 app:app
    ExecReload=/bin/kill -s HUP $MAINPID
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

11. **Start Service**
    ```bash
    sudo systemctl start pathology
    sudo systemctl enable pathology
    ```

12. **Configure Nginx**
    ```bash
    sudo nano /etc/nginx/sites-available/pathology
    ```
    
    Add:
    ```nginx
    server {
        listen 80;
        server_name your-domain.com;

        location / {
            include proxy_params;
            proxy_pass http://unix:/home/pathology/pathology-v1/pathology.sock;
        }

        location /static {
            alias /home/pathology/pathology-v1/static;
        }
    }
    ```

13. **Enable Site**
    ```bash
    sudo ln -s /etc/nginx/sites-available/pathology /etc/nginx/sites-enabled
    sudo nginx -t
    sudo systemctl restart nginx
    ```

14. **Setup SSL (Optional)**
    ```bash
    sudo apt install certbot python3-certbot-nginx
    sudo certbot --nginx -d your-domain.com
    ```

**Total Cost: $5-12/month**

---

## 🔧 Environment Variables

For all deployments, set these environment variables:

```bash
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
DATABASE_URL=postgresql://username:password@host:port/database
FLASK_ENV=production
```

---

## 📊 Cost Comparison

| Platform | Setup Difficulty | Monthly Cost | Best For |
|----------|------------------|--------------|----------|
| **DigitalOcean App Platform** | Easy | $20 | Beginners |
| **Azure App Service** | Medium | $15 | Microsoft ecosystem |
| **AWS Elastic Beanstalk** | Medium | $25 | AWS ecosystem |
| **VPS (DigitalOcean Droplet)** | Hard | $6-12 | Advanced users |

---

## 🛡️ Security Checklist

- [ ] Use strong SECRET_KEY (32+ characters)
- [ ] Use PostgreSQL in production (not SQLite)
- [ ] Enable HTTPS/SSL
- [ ] Set up regular database backups
- [ ] Use environment variables for sensitive data
- [ ] Keep dependencies updated
- [ ] Monitor application logs
- [ ] Set up firewall rules

---

## 📞 Support

If you encounter issues during deployment:

1. Check the application logs
2. Verify environment variables
3. Ensure database connection
4. Check firewall settings
5. Open an issue on GitHub

---

**Choose the deployment method that best fits your technical expertise and budget!**
