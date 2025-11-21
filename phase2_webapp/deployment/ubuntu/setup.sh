#!/bin/bash

################################################################################
# Healthrix Productivity System - Ubuntu Server 24.04 Setup Script
################################################################################
#
# This script automates the complete installation and configuration of the
# Healthrix Productivity System on Ubuntu Server 24.04 LTS.
#
# Usage:
#   sudo ./setup.sh
#
# What it does:
#   1. Installs system dependencies (Python, PostgreSQL, Redis, Nginx)
#   2. Creates application directory and user
#   3. Sets up database and creates tables
#   4. Configures systemd services
#   5. Sets up Nginx reverse proxy
#   6. Creates initial super admin user
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="healthrix"
APP_USER="healthrix"
APP_GROUP="healthrix"
APP_DIR="/opt/healthrix"
BACKEND_DIR="$APP_DIR/backend"
PYTHON_VERSION="3.11"
DB_NAME="healthrix"
DB_USER="healthrix_user"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

print_banner() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║          Healthrix Productivity System Installer            ║"
    echo "║                Ubuntu Server 24.04 LTS                       ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Main installation steps

step1_update_system() {
    log_info "Step 1: Updating system packages..."
    apt update -qq
    apt upgrade -y -qq
    log_success "System updated"
}

step2_install_dependencies() {
    log_info "Step 2: Installing system dependencies..."

    # Add deadsnakes PPA for Python 3.11
    add-apt-repository ppa:deadsnakes/ppa -y > /dev/null 2>&1
    apt update -qq

    # Install packages
    apt install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        postgresql-15 \
        postgresql-contrib-15 \
        redis-server \
        nginx \
        git \
        curl \
        build-essential \
        libpq-dev \
        supervisor > /dev/null 2>&1

    log_success "Dependencies installed"
}

step3_create_user() {
    log_info "Step 3: Creating application user..."

    if id "$APP_USER" &>/dev/null; then
        log_warning "User $APP_USER already exists"
    else
        useradd -r -s /bin/bash -d $APP_DIR -m $APP_USER
        log_success "User $APP_USER created"
    fi
}

step4_setup_database() {
    log_info "Step 4: Setting up PostgreSQL database..."

    # Start PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql > /dev/null 2>&1

    # Generate secure password
    DB_PASSWORD=$(generate_password)

    # Create database and user
    sudo -u postgres psql << EOF > /dev/null 2>&1
-- Drop existing if any
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Create fresh
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

    # Save credentials
    echo "$DB_PASSWORD" > /tmp/healthrix_db_password.txt
    chmod 600 /tmp/healthrix_db_password.txt

    log_success "Database configured (password saved to /tmp/healthrix_db_password.txt)"
}

step5_setup_redis() {
    log_info "Step 5: Setting up Redis..."

    # Configure Redis
    sed -i 's/^supervised no/supervised systemd/' /etc/redis/redis.conf

    # Start Redis
    systemctl start redis-server
    systemctl enable redis-server > /dev/null 2>&1

    log_success "Redis configured"
}

step6_setup_application() {
    log_info "Step 6: Setting up application..."

    # Create directory structure
    mkdir -p $APP_DIR/{backend,logs,backups}

    # Copy backend files (assuming script is run from deployment/ubuntu directory)
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    REPO_ROOT="$SCRIPT_DIR/../../.."

    if [ -d "$REPO_ROOT/phase2_webapp/backend" ]; then
        cp -r $REPO_ROOT/phase2_webapp/backend/* $BACKEND_DIR/
        log_success "Application files copied"
    else
        log_error "Backend directory not found at $REPO_ROOT/phase2_webapp/backend"
        exit 1
    fi

    # Set ownership
    chown -R $APP_USER:$APP_GROUP $APP_DIR
}

step7_setup_python_env() {
    log_info "Step 7: Setting up Python virtual environment..."

    # Create virtual environment
    sudo -u $APP_USER python${PYTHON_VERSION} -m venv $BACKEND_DIR/venv

    # Install dependencies
    sudo -u $APP_USER $BACKEND_DIR/venv/bin/pip install --upgrade pip > /dev/null 2>&1
    sudo -u $APP_USER $BACKEND_DIR/venv/bin/pip install -r $BACKEND_DIR/requirements.txt > /dev/null 2>&1

    log_success "Python environment configured"
}

step8_create_env_file() {
    log_info "Step 8: Creating environment configuration..."

    # Generate secret key
    SECRET_KEY=$(generate_password)

    # Read database password
    DB_PASSWORD=$(cat /tmp/healthrix_db_password.txt)

    # Create .env file
    cat > $BACKEND_DIR/.env << EOF
# Application Settings
APP_NAME=Healthrix Productivity System
APP_VERSION=2.0.0
ENVIRONMENT=production

# API Settings
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost","http://$(hostname -I | awk '{print $1}')"]

# Security
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME

# Redis
REDIS_URL=redis://localhost:6379/0

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Logging
LOG_LEVEL=info
EOF

    chown $APP_USER:$APP_GROUP $BACKEND_DIR/.env
    chmod 600 $BACKEND_DIR/.env

    log_success "Environment configuration created"
}

step9_initialize_database() {
    log_info "Step 9: Initializing database tables..."

    # Create initialization script
    cat > /tmp/init_db.py << 'EOF'
from app.db.session import engine, Base, SessionLocal
from app.models import User, UserRole, Department, TaskStandard, Activity, DailyMetric, PerformanceScore
from app.core.security import get_password_hash
from datetime import datetime

# Create tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")

# Create super admin
db = SessionLocal()
try:
    existing = db.query(User).filter(User.emp_id == 'ADMIN001').first()
    if not existing:
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
        print("Super admin created!")
    else:
        print("Super admin already exists")
finally:
    db.close()
EOF

    # Run initialization
    sudo -u $APP_USER bash << EOF
cd $BACKEND_DIR
source venv/bin/activate
python /tmp/init_db.py
EOF

    rm /tmp/init_db.py
    log_success "Database initialized"
}

step10_setup_systemd() {
    log_info "Step 10: Configuring systemd service..."

    cat > /etc/systemd/system/healthrix-backend.service << EOF
[Unit]
Description=Healthrix Productivity System Backend API
After=network.target postgresql.service redis-server.service
Requires=postgresql.service

[Service]
Type=notify
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/venv/bin"
EnvironmentFile=$BACKEND_DIR/.env
ExecStart=$BACKEND_DIR/venv/bin/uvicorn app.main:app \\
    --host 0.0.0.0 \\
    --port 8000 \\
    --workers 4 \\
    --log-level info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable healthrix-backend > /dev/null 2>&1
    systemctl start healthrix-backend

    log_success "Systemd service configured"
}

step11_setup_nginx() {
    log_info "Step 11: Configuring Nginx reverse proxy..."

    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}')

    cat > /etc/nginx/sites-available/healthrix << EOF
upstream healthrix_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $SERVER_IP localhost;

    client_max_body_size 10M;

    # API Endpoints
    location /api/ {
        proxy_pass http://healthrix_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API Documentation
    location /docs {
        proxy_pass http://healthrix_backend;
        proxy_set_header Host \$host;
    }

    location /redoc {
        proxy_pass http://healthrix_backend;
        proxy_set_header Host \$host;
    }

    location /openapi.json {
        proxy_pass http://healthrix_backend;
        proxy_set_header Host \$host;
    }

    # Health check
    location /health {
        proxy_pass http://healthrix_backend/api/v1/health;
        access_log off;
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/healthrix /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default

    # Test and reload Nginx
    nginx -t
    systemctl reload nginx

    log_success "Nginx configured"
}

step12_setup_firewall() {
    log_info "Step 12: Configuring firewall..."

    if command -v ufw &> /dev/null; then
        ufw --force enable
        ufw allow 22/tcp comment 'SSH'
        ufw allow 80/tcp comment 'HTTP'
        ufw allow 443/tcp comment 'HTTPS'
        log_success "Firewall configured"
    else
        log_warning "UFW not found, skipping firewall configuration"
    fi
}

print_summary() {
    SERVER_IP=$(hostname -I | awk '{print $1}')
    DB_PASSWORD=$(cat /tmp/healthrix_db_password.txt 2>/dev/null || echo "N/A")

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║                  Installation Complete! 🎉                   ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    log_success "Healthrix Productivity System is now installed and running!"
    echo ""
    echo "📋 Installation Summary:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  🌐 API URL:           http://$SERVER_IP/api/v1"
    echo "  📚 API Docs:          http://$SERVER_IP/docs"
    echo "  📖 ReDoc:             http://$SERVER_IP/redoc"
    echo "  ❤️  Health Check:      http://$SERVER_IP/health"
    echo ""
    echo "  👤 Super Admin Credentials:"
    echo "     Email:             admin@healthrix.local"
    echo "     Password:          Admin@123"
    echo "     ⚠️  CHANGE PASSWORD IMMEDIATELY!"
    echo ""
    echo "  🗄️  Database:"
    echo "     Name:              $DB_NAME"
    echo "     User:              $DB_USER"
    echo "     Password:          $DB_PASSWORD"
    echo "     Password saved to: /tmp/healthrix_db_password.txt"
    echo ""
    echo "  📁 Application Directory: $APP_DIR"
    echo "  🔧 Service Name:          healthrix-backend"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 Useful Commands:"
    echo ""
    echo "  # Check service status:"
    echo "  sudo systemctl status healthrix-backend"
    echo ""
    echo "  # View logs:"
    echo "  sudo journalctl -u healthrix-backend -f"
    echo ""
    echo "  # Restart service:"
    echo "  sudo systemctl restart healthrix-backend"
    echo ""
    echo "  # Test API:"
    echo "  curl http://$SERVER_IP/health"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    log_info "For detailed documentation, see: $APP_DIR/UBUNTU_DEPLOYMENT.md"
    echo ""
}

# Main execution
main() {
    print_banner
    check_root

    log_info "Starting Healthrix installation..."
    echo ""

    step1_update_system
    step2_install_dependencies
    step3_create_user
    step4_setup_database
    step5_setup_redis
    step6_setup_application
    step7_setup_python_env
    step8_create_env_file
    step9_initialize_database
    step10_setup_systemd
    step11_setup_nginx
    step12_setup_firewall

    # Wait a moment for services to stabilize
    sleep 2

    print_summary
}

# Run main function
main "$@"
