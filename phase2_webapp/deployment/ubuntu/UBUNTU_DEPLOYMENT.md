# Healthrix Deployment on Ubuntu Server 24.04

Complete guide for deploying the Healthrix Productivity System on Ubuntu Server 24.04 LTS for local development and production use.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (Automated Setup)](#quick-start-automated-setup)
- [Manual Installation](#manual-installation)
- [Configuration](#configuration)
- [Starting Services](#starting-services)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **OS**: Ubuntu Server 24.04 LTS (Recommended) or 22.04 LTS
- **CPU**: 2+ cores (4+ cores recommended for production)
- **RAM**: 4GB minimum (8GB+ recommended for production)
- **Storage**: 20GB minimum (50GB+ recommended for production)
- **Network**: Internet connection for package downloads

### User Requirements

- User with sudo privileges
- SSH access (for remote deployment)
- Basic Linux command line knowledge

---

## Quick Start (Automated Setup)

### 1. Download the Setup Script

```bash
# Clone the repository
git clone https://github.com/yourusername/healthrix.git
cd healthrix/phase2_webapp/deployment/ubuntu

# Make scripts executable
chmod +x setup.sh
chmod +x install_dependencies.sh
chmod +x configure_services.sh
```

### 2. Run Automated Setup

```bash
# Full installation (recommended for first-time setup)
sudo ./setup.sh

# Or run individual steps
sudo ./install_dependencies.sh      # Install system dependencies
sudo ./configure_services.sh        # Configure systemd services and nginx
```

### 3. Configure Environment

```bash
# Edit environment variables
sudo nano /opt/healthrix/backend/.env

# Set your database password, secret keys, etc.
# See Configuration section below for details
```

### 4. Start Services

```bash
# Start all services
sudo systemctl start healthrix-backend
sudo systemctl start healthrix-nginx

# Enable auto-start on boot
sudo systemctl enable healthrix-backend
sudo systemctl enable nginx
```

### 5. Verify Installation

```bash
# Check service status
sudo systemctl status healthrix-backend
sudo systemctl status nginx

# Test API
curl http://localhost/api/v1/auth/health
# Expected: {"status": "healthy"}

# Access API documentation
# Open browser: http://your-server-ip/docs
```

✅ **Installation Complete!** The Healthrix API is now running.

---

## Manual Installation

If you prefer manual installation or need custom configuration:

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Python 3.11+

```bash
# Add deadsnakes PPA for latest Python
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
```

### Step 3: Install PostgreSQL

```bash
# Install PostgreSQL 15
sudo apt install -y postgresql-15 postgresql-contrib-15

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE healthrix;
CREATE USER healthrix_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE healthrix TO healthrix_user;
ALTER DATABASE healthrix OWNER TO healthrix_user;
\q
EOF
```

### Step 4: Install Redis (for caching and real-time features)

```bash
sudo apt install -y redis-server

# Configure Redis
sudo sed -i 's/^supervised no/supervised systemd/' /etc/redis/redis.conf

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify
redis-cli ping
# Expected: PONG
```

### Step 5: Install Nginx

```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 6: Setup Application

```bash
# Create application directory
sudo mkdir -p /opt/healthrix
sudo chown $USER:$USER /opt/healthrix

# Copy application files
cp -r phase2_webapp/backend /opt/healthrix/

# Create Python virtual environment
cd /opt/healthrix/backend
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 7: Configure Environment Variables

```bash
# Create .env file
cat > /opt/healthrix/backend/.env << 'EOF'
# Application Settings
APP_NAME=Healthrix Productivity System
APP_VERSION=2.0.0
ENVIRONMENT=production

# API Settings
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost"]

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://healthrix_user:your_secure_password_here@localhost/healthrix

# Redis
REDIS_URL=redis://localhost:6379/0

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Logging
LOG_LEVEL=info
EOF

# Secure the .env file
chmod 600 /opt/healthrix/backend/.env
```

### Step 8: Initialize Database

```bash
# Activate virtual environment
cd /opt/healthrix/backend
source venv/bin/activate

# Run database migrations (create tables)
python -c "
from app.db.session import engine, Base
from app.models import User, Department, TaskStandard, Activity, DailyMetric, PerformanceScore
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"
```

### Step 9: Create Super Admin User

```bash
# Create initial super admin
python -c "
from app.db.session import SessionLocal
from app.models import User, UserRole
from app.core.security import get_password_hash
from datetime import datetime

db = SessionLocal()
super_admin = User(
    emp_id='ADMIN001',
    email='admin@healthrix.local',
    hashed_password=get_password_hash('Admin@123'),
    name='System Administrator',
    role=UserRole.SUPER_ADMIN,
    is_active=True,
    hire_date=datetime.utcnow()
)
db.add(super_admin)
db.commit()
print('Super admin created!')
print('Email: admin@healthrix.local')
print('Password: Admin@123')
print('IMPORTANT: Change this password immediately!')
db.close()
"
```

---

## Configuration

### Systemd Service Configuration

Create systemd service file for automatic startup:

```bash
sudo nano /etc/systemd/system/healthrix-backend.service
```

```ini
[Unit]
Description=Healthrix Productivity System Backend API
After=network.target postgresql.service redis-server.service
Requires=postgresql.service

[Service]
Type=notify
User=healthrix
Group=healthrix
WorkingDirectory=/opt/healthrix/backend
Environment="PATH=/opt/healthrix/backend/venv/bin"
EnvironmentFile=/opt/healthrix/backend/.env
ExecStart=/opt/healthrix/backend/venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Nginx Reverse Proxy Configuration

```bash
sudo nano /etc/nginx/sites-available/healthrix
```

```nginx
upstream healthrix_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-server-domain.com;  # Change this

    client_max_body_size 10M;

    # API Endpoints
    location /api/ {
        proxy_pass http://healthrix_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # WebSocket support (for real-time features)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API Documentation
    location /docs {
        proxy_pass http://healthrix_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /redoc {
        proxy_pass http://healthrix_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /openapi.json {
        proxy_pass http://healthrix_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health check
    location /health {
        proxy_pass http://healthrix_backend;
        access_log off;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/healthrix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS Configuration (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-server-domain.com

# Auto-renewal is configured automatically
```

---

## Starting Services

### Start Backend Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start healthrix-backend

# Enable auto-start
sudo systemctl enable healthrix-backend

# Check status
sudo systemctl status healthrix-backend

# View logs
sudo journalctl -u healthrix-backend -f
```

### Start Nginx

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

---

## Monitoring & Maintenance

### Check Service Status

```bash
# Backend API
sudo systemctl status healthrix-backend

# Database
sudo systemctl status postgresql

# Nginx
sudo systemctl status nginx

# Redis
sudo systemctl status redis-server
```

### View Logs

```bash
# Backend logs
sudo journalctl -u healthrix-backend -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Database Backup

```bash
# Create backup script
sudo nano /opt/healthrix/scripts/backup_database.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/healthrix/backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U healthrix_user healthrix | gzip > $BACKUP_DIR/healthrix_$TIMESTAMP.sql.gz
# Keep only last 30 days
find $BACKUP_DIR -name "healthrix_*.sql.gz" -mtime +30 -delete
echo "Backup completed: healthrix_$TIMESTAMP.sql.gz"
```

```bash
chmod +x /opt/healthrix/scripts/backup_database.sh

# Add to cron for daily backups
crontab -e
# Add line:
0 2 * * * /opt/healthrix/scripts/backup_database.sh
```

### Performance Monitoring

```bash
# CPU and Memory usage
htop

# API performance
curl http://localhost/api/v1/health

# Database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='healthrix';"

# Disk usage
df -h
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
sudo journalctl -u healthrix-backend -n 50 --no-pager

# Check if port is already in use
sudo netstat -tulpn | grep 8000

# Verify virtual environment
source /opt/healthrix/backend/venv/bin/activate
python --version  # Should be 3.11+
```

### Database Connection Errors

```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U healthrix_user -d healthrix -h localhost

# Check database exists
sudo -u postgres psql -l | grep healthrix
```

### Permission Errors

```bash
# Fix ownership
sudo chown -R healthrix:healthrix /opt/healthrix

# Fix .env permissions
sudo chmod 600 /opt/healthrix/backend/.env
```

### Nginx 502 Bad Gateway

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Verify proxy settings
sudo nginx -t
```

### High Memory Usage

```bash
# Reduce worker processes
# Edit .env or service file
WORKERS=2  # Reduce from 4

# Restart service
sudo systemctl restart healthrix-backend
```

---

## Security Best Practices

1. **Change Default Passwords**
   ```bash
   # Change super admin password via API
   curl -X POST http://localhost/api/v1/users/ADMIN001/change-password \
     -H "Content-Type: application/json" \
     -d '{"old_password":"Admin@123","new_password":"NewSecure@Pass123"}'
   ```

2. **Enable Firewall**
   ```bash
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw enable
   ```

3. **Regular Updates**
   ```bash
   # System updates
   sudo apt update && sudo apt upgrade -y

   # Python dependencies
   cd /opt/healthrix/backend
   source venv/bin/activate
   pip list --outdated
   ```

4. **Monitor Logs**
   ```bash
   # Setup log rotation
   sudo nano /etc/logrotate.d/healthrix
   ```

---

## Performance Tuning

### PostgreSQL Optimization

```bash
sudo nano /etc/postgresql/15/main/postgresql.conf
```

```conf
# Adjust based on your RAM (example for 8GB RAM)
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 16MB
max_connections = 100
```

### Uvicorn Workers

Adjust workers based on CPU cores:
```
Workers = (2 × CPU cores) + 1
```

For 4 CPU cores: 9 workers

---

## Next Steps

- **Frontend Setup**: Deploy React/Vue frontend (see Frontend Guide)
- **Monitoring**: Setup Prometheus and Grafana (see Phase 3)
- **Scaling**: Configure load balancing for high availability
- **Backup Strategy**: Implement automated backup solution

---

## Support & Resources

- **Documentation**: https://your-docs-site.com
- **GitHub Issues**: https://github.com/yourusername/healthrix/issues
- **Email Support**: support@healthrix.local

---

**Deployment Complete! 🎉**

Access your API at: `http://your-server-ip/docs`

Default super admin credentials:
- Email: `admin@healthrix.local`
- Password: `Admin@123` (⚠️ **CHANGE IMMEDIATELY!**)
