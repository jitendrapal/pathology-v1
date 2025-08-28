# 🌐 **Digital Ocean Deployment Guide for Pathology Lab Database**

## 🚀 **Complete Guide: Deploy Your Database to Digital Ocean Server**

Your question about accessing the database from Digital Ocean with a different domain is perfectly achievable! Here's the complete solution:

---

## 🎯 **What You'll Achieve:**

### **After Deployment:**
```
🌍 Access from anywhere: https://your-domain.com
📊 Real-time database viewing: https://your-domain.com/db-viewer/
📱 Mobile access: Works on phones/tablets
🔒 Secure authentication: Username/password protected
💾 Your SQLite database: Accessible globally
```

---

## 🔧 **Step-by-Step Deployment Process:**

### **Step 1: Create Digital Ocean Droplet**
```
1. Go to Digital Ocean dashboard
2. Click "Create" → "Droplets"
3. Choose Ubuntu 22.04 LTS
4. Select plan:
   - Basic: $6/month (1GB RAM) - Good for small labs
   - Basic: $12/month (2GB RAM) - Better performance
5. Choose datacenter region (closest to you)
6. Add SSH key or use password authentication
7. Choose hostname: pathology-lab
8. Click "Create Droplet"
```

### **Step 2: Get Your Server Details**
```
After creation, you'll get:
- IP Address: e.g., 143.198.123.45
- SSH Access: ssh root@143.198.123.45
- Domain: You can use IP or set up custom domain
```

### **Step 3: Connect to Your Server**
```bash
# Connect via SSH (Windows: use PuTTY or PowerShell)
ssh root@your-droplet-ip

# Example:
ssh root@143.198.123.45
```

### **Step 4: Install Required Software**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git nginx supervisor -y

# Create application directory
sudo mkdir -p /var/www/pathology-lab
cd /var/www/pathology-lab
```

### **Step 5: Upload Your Application**
```bash
# From your local computer, upload files
scp -r pathology/ root@your-droplet-ip:/var/www/pathology-lab/

# Or use git (if you have repository)
git clone https://github.com/your-username/pathology-lab.git .

# Upload your database
scp data/pathology.db root@your-droplet-ip:/var/www/pathology-lab/data/
```

### **Step 6: Set Up Python Environment**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask sqlalchemy pandas gunicorn

# Set permissions
sudo chown -R www-data:www-data /var/www/pathology-lab
sudo chmod -R 755 /var/www/pathology-lab
```

---

## 🌍 **Domain Configuration Options:**

### **Option 1: Use Digital Ocean IP (Immediate)**
```
Access URLs:
Main App: http://143.198.123.45
Database: http://143.198.123.45/db-viewer/

Pros: Works immediately
Cons: Hard to remember IP address
```

### **Option 2: Digital Ocean Domain (Free)**
```
Digital Ocean provides free subdomain:
your-droplet-name.digitalocean.com

Access URLs:
Main App: http://pathology-lab.digitalocean.com
Database: http://pathology-lab.digitalocean.com/db-viewer/
```

### **Option 3: Custom Domain (Professional)**
```
Buy domain (e.g., yourlab.com) and point to Digital Ocean:

1. Buy domain from Namecheap, GoDaddy, etc.
2. In domain settings, set DNS:
   - A Record: @ → your-droplet-ip
   - A Record: www → your-droplet-ip

Access URLs:
Main App: https://yourlab.com
Database: https://yourlab.com/db-viewer/
```

---

## 🔧 **Server Configuration:**

### **Create Systemd Service:**
```bash
# Create service file for database viewer
sudo tee /etc/systemd/system/pathology-db-viewer.service > /dev/null << EOF
[Unit]
Description=Pathology Lab Database Viewer
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/pathology-lab
Environment="PATH=/var/www/pathology-lab/venv/bin"
ExecStart=/var/www/pathology-lab/venv/bin/python production_web_database_viewer.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
```

### **Configure Nginx:**
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/pathology-lab > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com your-droplet-ip;

    # Main application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Database viewer
    location /db-viewer/ {
        proxy_pass http://127.0.0.1:5001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files
    location /static/ {
        alias /var/www/pathology-lab/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/pathology-lab /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### **Start Services:**
```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable pathology-db-viewer
sudo systemctl start pathology-db-viewer
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status pathology-db-viewer
sudo systemctl status nginx
```

---

## 🔒 **Security Configuration:**

### **Set Environment Variables:**
```bash
# Create environment file
sudo tee /etc/environment >> /dev/null << EOF
DB_ADMIN_USER="admin"
DB_ADMIN_PASS="your_strong_password_here"
SECRET_KEY="your-secret-key-change-this"
FLASK_HOST="127.0.0.1"
FLASK_PORT="5001"
EOF

# Reload environment
source /etc/environment
```

### **Configure Firewall:**
```bash
# Set up UFW firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw --force enable
```

### **Install SSL Certificate (HTTPS):**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 **Access Your Database:**

### **Web Interface Access:**
```
URL: https://your-domain.com/db-viewer/
Login: admin / your_password

Features:
✅ Real-time statistics dashboard
✅ Patient data browsing
✅ Test results viewing
✅ Payment tracking
✅ CSV export functionality
✅ Mobile-responsive design
```

### **API Access:**
```
Base URL: https://your-domain.com/db-viewer/api/

Endpoints:
GET /api/database-info     - Database information
GET /api/table-data/patient - Patient data
GET /api/real-time-stats   - Live statistics
GET /api/export/patient    - Export patient CSV
```

---

## 📱 **Multi-Device Access:**

### **From Computer:**
```
URL: https://your-domain.com/db-viewer/
Features: Full desktop interface
```

### **From Mobile:**
```
URL: https://your-domain.com/db-viewer/
Features: Mobile-optimized interface
```

### **From Tablet:**
```
URL: https://your-domain.com/db-viewer/
Features: Touch-friendly interface
```

---

## 💰 **Cost Analysis:**

### **Digital Ocean Costs:**
```
Basic Droplet: $6/month (1GB RAM, 25GB SSD)
Standard Droplet: $12/month (2GB RAM, 50GB SSD)
Domain (optional): $10-15/year
SSL Certificate: Free (Let's Encrypt)
Bandwidth: 1TB included

Total Monthly Cost: $6-12
Total Yearly Cost: $72-144 + domain
```

### **Compared to Alternatives:**
```
AWS RDS: $15-50/month
Google Cloud SQL: $10-40/month
Azure Database: $15-45/month
Dedicated Server: $50-200/month

Your Solution: $6-12/month (much cheaper!)
```

---

## 🛠️ **Management Commands:**

### **Service Management:**
```bash
# Check service status
sudo systemctl status pathology-db-viewer

# Restart service
sudo systemctl restart pathology-db-viewer

# View logs
sudo journalctl -u pathology-db-viewer -f

# Stop/start service
sudo systemctl stop pathology-db-viewer
sudo systemctl start pathology-db-viewer
```

### **Database Management:**
```bash
# Access database directly
cd /var/www/pathology-lab
source venv/bin/activate
python backup_system.py info

# Create backup
python backup_system.py backup

# View database
sqlite3 data/pathology.db
```

### **Update Application:**
```bash
# Upload new files from local computer
scp -r pathology/ root@your-droplet-ip:/var/www/pathology-lab/

# Restart services
sudo systemctl restart pathology-db-viewer nginx
```

---

## 🎯 **Real-World Usage Examples:**

### **Lab Owner Monitoring:**
```
Location: Home office
URL: https://yourlab.com/db-viewer/
View: Daily patient count, revenue, pending tests
Export: Financial reports for accounting
Time: 24/7 access
```

### **Remote Lab Management:**
```
Location: Multiple lab branches
URL: Same URL from all locations
View: Centralized patient database
Manage: Test results, billing, reports
Benefits: Unified data access
```

### **Mobile Operations:**
```
Device: Smartphone/tablet
URL: https://yourlab.com/db-viewer/
Features: Patient lookup, test viewing
Use Case: Field work, home visits
```

---

## 🎉 **Success Checklist:**

### **Deployment Complete When:**
```
✅ Can access https://your-domain.com/db-viewer/
✅ Login works with your credentials
✅ Can see real-time lab statistics
✅ Can browse patient data
✅ Can export CSV files
✅ Mobile access works properly
✅ HTTPS (SSL) is active
✅ Services auto-start on reboot
```

### **Testing Your Deployment:**
```bash
# Test from different devices
curl -I https://your-domain.com/db-viewer/

# Check SSL certificate
openssl s_client -connect your-domain.com:443

# Monitor logs
sudo tail -f /var/log/nginx/access.log
sudo journalctl -u pathology-db-viewer -f
```

**Your pathology lab database is now accessible globally via Digital Ocean!** 🌍✨

**Access from anywhere**: `https://your-domain.com/db-viewer/` 🌐

**Professional, secure, and cost-effective solution!** 🇮🇳💪
