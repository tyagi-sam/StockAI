#!/bin/bash

# Stock AI EC2 Setup Script
# Run this script on your EC2 instance to set up the production environment

set -e  # Exit on any error

echo "🚀 Starting Stock AI EC2 Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root"
    exit 1
fi

# Check if we're on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
    print_warning "This script is designed for Ubuntu. Other distributions may need modifications."
fi

print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

print_status "Installing essential packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    nginx \
    certbot \
    python3-certbot-nginx \
    htop \
    iotop \
    nethogs

print_status "Installing Docker..."
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

print_status "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

print_status "Verifying installations..."
docker --version
docker-compose --version

print_status "Setting up project directory..."
cd /home/ubuntu

# Check if repository already exists
if [ -d "stock-ai" ]; then
    print_warning "stock-ai directory already exists. Updating..."
    cd stock-ai
    git pull origin main
else
    print_status "Cloning repository..."
    git clone https://github.com/yourusername/stock-ai.git
    cd stock-ai
fi

print_status "Setting up environment..."
if [ ! -f ".env" ]; then
    cp env.production.example .env
    print_warning "Please edit .env file with your production values:"
    echo "   nano .env"
    echo ""
    echo "Required variables:"
    echo "   - POSTGRES_PASSWORD (strong password)"
    echo "   - REDIS_PASSWORD (strong password)"
    echo "   - JWT_SECRET (32+ characters)"
    echo "   - FERNET_KEY (base64 encoded)"
    echo "   - GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
    echo "   - ZERODHA_API_KEY and ZERODHA_API_SECRET"
    echo "   - SMTP settings for Zoho Mail"
    echo "   - FRONTEND_URL=https://stock-satta.online"
    echo "   - BACKEND_CORS_ORIGINS=https://stock-satta.online"
    echo ""
    read -p "Press Enter after editing .env file..."
else
    print_status ".env file already exists"
fi

print_status "Setting up monitoring scripts..."

# Create monitoring script
cat > /home/ubuntu/monitor.sh << 'EOF'
#!/bin/bash
echo "=== Stock AI System Status ==="
echo "Date: $(date)"
echo "Uptime: $(uptime)"
echo "Memory: $(free -h)"
echo "Disk: $(df -h /)"
echo "Docker Status:"
docker-compose -f /home/ubuntu/stock-ai/docker-compose.prod.yml ps
echo "Health Checks:"
curl -s http://localhost/health || echo "Frontend health check failed"
curl -s http://localhost:8000/health || echo "Backend health check failed"
EOF

chmod +x /home/ubuntu/monitor.sh

# Create backup script
cat > /home/ubuntu/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
docker-compose -f /home/ubuntu/stock-ai/docker-compose.prod.yml exec -T postgres pg_dump -U stock_ai_user stock_ai > $BACKUP_DIR/db_backup_$DATE.sql

# Environment backup
cp /home/ubuntu/stock-ai/.env $BACKUP_DIR/env_backup_$DATE

# Compress backups
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $BACKUP_DIR db_backup_$DATE.sql env_backup_$DATE

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.tar.gz"
EOF

chmod +x /home/ubuntu/backup.sh

print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/stock-ai << EOF
/home/ubuntu/stock-ai/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        docker-compose -f /home/ubuntu/stock-ai/docker-compose.prod.yml restart
    endscript
}
EOF

print_status "Setting up automatic backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup.sh") | crontab -

print_status "Configuring nginx..."
sudo tee /etc/nginx/sites-available/stock-ai << 'EOF'
server {
    listen 80;
    server_name stock-satta.online www.stock-satta.online;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name stock-satta.online www.stock-satta.online;

    ssl_certificate /etc/letsencrypt/live/stock-satta.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/stock-satta.online/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health checks
    location /health {
        proxy_pass http://localhost:80;
        access_log off;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/stock-ai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

print_status "Testing nginx configuration..."
sudo nginx -t

print_status "Starting nginx..."
sudo systemctl enable nginx
sudo systemctl restart nginx

print_status "Setting up SSL certificate..."
print_warning "Make sure your domain (stock-satta.online) is pointing to this EC2 instance before proceeding."
read -p "Press Enter when domain is configured..."

# Get SSL certificate
sudo certbot certonly --standalone -d stock-satta.online -d www.stock-satta.online --non-interactive --agree-tos --email your-email@example.com

print_status "Testing certificate renewal..."
sudo certbot renew --dry-run

print_status "EC2 setup completed!"
print_status ""
print_status "Next steps:"
echo "1. Edit .env file: nano /home/ubuntu/stock-ai/.env"
echo "2. Deploy application: cd /home/ubuntu/stock-ai && ./deploy.sh"
echo "3. Test the application: https://stock-satta.online"
echo ""
print_status "Useful commands:"
echo "  Monitor system: /home/ubuntu/monitor.sh"
echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Backup data: /home/ubuntu/backup.sh"
echo "  Update app: cd /home/ubuntu/stock-ai && git pull && ./deploy.sh"
echo ""
print_status "Remember to:"
echo "  - Configure AWS Security Groups (ports 22, 80, 443, 8000)"
echo "  - Set up domain DNS records in Namecheap"
echo "  - Test SSL certificate"
echo "  - Monitor application health"

print_status "Setup completed successfully! 🎉" 