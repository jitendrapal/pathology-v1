#!/bin/bash
# Digital Ocean Deployment Script for Pathology Lab Software

echo "🚀 Digital Ocean Deployment Script"
echo "=================================="

# Configuration
APP_NAME="pathology-lab"
APP_DIR="/var/www/$APP_NAME"
DOMAIN="your-domain.com"  # Change this to your domain or use IP
SERVER_IP="your-droplet-ip"  # Change this to your droplet IP

echo "📋 Deployment Configuration:"
echo "App Name: $APP_NAME"
echo "App Directory: $APP_DIR"
echo "Domain/IP: $DOMAIN"
echo ""

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p $APP_DIR
cd $APP_DIR

# Clone or upload your application
echo "📥 Setting up application files..."
# Option 1: If you have git repository
# sudo git clone https://github.com/your-username/pathology-lab.git .

# Option 2: Manual file upload (you'll need to upload files manually)
echo "Please upload your application files to: $APP_DIR"
echo "Required files:"
echo "  - app.py"
echo "  - web_database_viewer.py"
echo "  - secure_web_database_viewer.py"
echo "  - templates/"
echo "  - static/"
echo "  - data/ (with your database)"
echo ""

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
sudo python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install flask sqlalchemy pandas gunicorn

# Create requirements.txt for future deployments
cat > requirements.txt << EOF
Flask==2.3.3
SQLAlchemy==2.0.21
pandas==2.1.1
gunicorn==21.2.0
Werkzeug==2.3.7
EOF

# Install requirements
pip install -r requirements.txt

# Create data directory and set permissions
echo "📊 Setting up database directory..."
sudo mkdir -p $APP_DIR/data
sudo mkdir -p $APP_DIR/data/backups
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# Create Gunicorn configuration
echo "⚙️ Creating Gunicorn configuration..."
cat > gunicorn_config.py << EOF
# Gunicorn configuration for pathology lab
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
user = "www-data"
group = "www-data"
tmp_upload_dir = None
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
EOF

# Create log directory for Gunicorn
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn

# Create systemd service for main application
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/pathology-lab.service > /dev/null << EOF
[Unit]
Description=Pathology Lab Management System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn_config.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for database viewer
sudo tee /etc/systemd/system/pathology-db-viewer.service > /dev/null << EOF
[Unit]
Description=Pathology Lab Database Viewer
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python web_database_viewer.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
echo "🌐 Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN $SERVER_IP;

    # Main application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
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
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration has errors"
    exit 1
fi

# Create firewall rules
echo "🔥 Setting up firewall..."
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw --force enable

# Start and enable services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable pathology-lab
sudo systemctl enable pathology-db-viewer
sudo systemctl enable nginx

sudo systemctl start pathology-lab
sudo systemctl start pathology-db-viewer
sudo systemctl restart nginx

# Check service status
echo "📊 Service Status:"
echo "=================="
sudo systemctl status pathology-lab --no-pager -l
echo ""
sudo systemctl status pathology-db-viewer --no-pager -l
echo ""
sudo systemctl status nginx --no-pager -l

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "🔗 Access URLs:"
echo "Main Application: http://$DOMAIN"
echo "Database Viewer:  http://$DOMAIN/db-viewer/"
echo ""
echo "📋 Next Steps:"
echo "1. Upload your application files to: $APP_DIR"
echo "2. Upload your database to: $APP_DIR/data/pathology.db"
echo "3. Restart services: sudo systemctl restart pathology-lab pathology-db-viewer"
echo "4. Check logs: sudo journalctl -u pathology-lab -f"
echo ""
echo "🔧 Useful Commands:"
echo "View logs: sudo journalctl -u pathology-lab -f"
echo "Restart app: sudo systemctl restart pathology-lab"
echo "Restart db viewer: sudo systemctl restart pathology-db-viewer"
echo "Restart nginx: sudo systemctl restart nginx"
echo ""
echo "🛡️ Security:"
echo "- Firewall is enabled (ports 22, 80, 443)"
echo "- Services run as www-data user"
echo "- Consider setting up SSL certificate"
echo ""
echo "📁 Important Directories:"
echo "App files: $APP_DIR"
echo "Database: $APP_DIR/data/pathology.db"
echo "Logs: /var/log/gunicorn/"
echo "Nginx config: /etc/nginx/sites-available/$APP_NAME"
EOF
