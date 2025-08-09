# EC2 Production Deployment Guide for Stock AI

This guide covers deploying your Stock AI application to an EC2 instance with domain configuration and SSL certificates.

## 🏗️ **Infrastructure Overview**

```
Internet → Domain (Namecheap) → EC2 Instance → Docker Containers
                                    ↓
                            [Nginx → Frontend → Backend → Database]
```

## 📋 **Prerequisites Checklist**

- [ ] EC2 instance running (Ubuntu 22.04 LTS recommended)
- [ ] Domain from Namecheap (`stock-satta.online`)
- [ ] Zoho Mail configured (`noreply@stock-satta.online`)
- [ ] SSH access to EC2 instance
- [ ] Security groups configured

## 🚀 **Step 1: EC2 Instance Setup**

### **1.1 Connect to Your EC2 Instance**

```bash
# Connect via SSH (replace with your key and IP)
ssh -i your-key.pem ubuntu@your-ec2-ip

# Or if using .pem file
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### **1.2 Update System and Install Dependencies**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

### **1.3 Configure Firewall (Security Groups)**

In AWS Console:
1. **Go to EC2 → Security Groups**
2. **Select your instance's security group**
3. **Add these inbound rules**:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | Your IP | SSH access |
| HTTP | TCP | 80 | 0.0.0.0/0 | Web traffic |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Secure web traffic |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 | Backend API |

## 🌐 **Step 2: Domain Configuration (Namecheap)**

### **2.1 Point Domain to EC2**

1. **Get your EC2 public IP**:
   ```bash
   curl ifconfig.me
   # or check in AWS Console
   ```

2. **Configure Namecheap DNS**:
   - Log into Namecheap
   - Go to **Domain List** → **Manage** → **Advanced DNS**
   - Add these records:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A | @ | YOUR_EC2_IP | 300 |
| A | www | YOUR_EC2_IP | 300 |
| CNAME | api | YOUR_EC2_IP | 300 |

### **2.2 Verify Domain Propagation**

```bash
# Check if domain points to your EC2
nslookup stock-satta.online
dig stock-satta.online
```

## 🔧 **Step 3: Application Deployment**

### **3.1 Clone Your Repository**

```bash
# On your EC2 instance
cd /home/ubuntu
git clone https://github.com/yourusername/stock-ai.git
cd stock-ai
```

### **3.2 Create Production Environment**

```bash
# Copy production environment template
cp env.production.example .env

# Edit with your production values
nano .env
```

**Required .env values for production:**
```bash
# Database
POSTGRES_USER=stock_ai_user
POSTGRES_PASSWORD=your_strong_postgres_password
DATABASE_URL=postgresql://stock_ai_user:your_strong_postgres_password@postgres:5432/stock_ai

# Redis
REDIS_PASSWORD=your_strong_redis_password
REDIS_URL=redis://:your_strong_redis_password@redis:6379

# Security
JWT_SECRET=your_very_long_random_secret_here
FERNET_KEY=your_base64_encoded_32_byte_key

# APIs
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
ZERODHA_API_KEY=your_zerodha_api_key
ZERODHA_API_SECRET=your_zerodha_api_secret

# Email (Zoho Mail)
SMTP_HOST=smtp.zoho.com
SMTP_PORT=587
SMTP_USERNAME=noreply@stock-satta.online
SMTP_PASSWORD=your_zoho_password
SMTP_TLS=true
SMTP_SSL=false
FROM_EMAIL=noreply@stock-satta.online
FROM_NAME=StockAI

# Domain
FRONTEND_URL=https://stock-satta.online
BACKEND_CORS_ORIGINS=https://stock-satta.online,https://www.stock-satta.online
ENVIRONMENT=production
```

### **3.3 Deploy Application**

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy to production
./deploy.sh
```

### **3.4 Verify Deployment**

```bash
# Check if services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Test health endpoints
curl http://localhost/health
curl http://localhost:8000/health
```

## 🔒 **Step 4: SSL Certificate Setup**

### **4.1 Install Certbot**

```bash
# Install Certbot
sudo apt install -y certbot

# Get SSL certificate
sudo certbot certonly --standalone -d stock-satta.online -d www.stock-satta.online

# Test certificate renewal
sudo certbot renew --dry-run
```

### **4.2 Configure Nginx with SSL**

Create nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/stock-ai
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name stock-satta.online www.stock-satta.online;
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
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/stock-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📊 **Step 5: Monitoring & Maintenance**

### **5.1 Set Up Monitoring**

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

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
```

### **5.2 Set Up Log Rotation**

```bash
# Create log rotation config
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
```

### **5.3 Set Up Automatic Backups**

```bash
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

# Add to crontab (daily backup at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup.sh") | crontab -
```

## 🔄 **Step 6: Update Process**

### **6.1 Update Application**

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Navigate to project directory
cd /home/ubuntu/stock-ai

# Pull latest changes
git pull origin main

# Rebuild and deploy
./deploy.sh
```

### **6.2 Rollback Process**

```bash
# If something goes wrong, rollback
git checkout HEAD~1
./deploy.sh
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Domain Not Resolving**
```bash
# Check DNS propagation
nslookup stock-satta.online
dig stock-satta.online

# Check if nginx is running
sudo systemctl status nginx
```

#### **2. SSL Certificate Issues**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew
```

#### **3. Docker Issues**
```bash
# Check Docker status
sudo systemctl status docker

# Check container logs
docker-compose -f docker-compose.prod.yml logs

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

#### **4. Database Issues**
```bash
# Check database connection
docker-compose -f docker-compose.prod.yml exec backend python -c "
import asyncio
import asyncpg
async def test():
    try:
        conn = await asyncpg.connect('postgresql://user:pass@postgres:5432/stock_ai')
        print('Database connection successful')
        await conn.close()
    except Exception as e:
        print(f'Database connection failed: {e}')
asyncio.run(test())
"
```

## 📈 **Performance Optimization**

### **1. EC2 Instance Optimization**
- Use t3.medium or larger for production
- Enable CloudWatch monitoring
- Set up auto-scaling if needed

### **2. Database Optimization**
```sql
-- Add indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_searches_timestamp ON searches(timestamp);
```

### **3. Nginx Optimization**
```nginx
# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied any;
gzip_comp_level 6;
```

## 🎯 **Final Checklist**

- [ ] EC2 instance configured
- [ ] Domain pointing to EC2
- [ ] SSL certificate installed
- [ ] Application deployed
- [ ] Email configured (Zoho Mail)
- [ ] Monitoring set up
- [ ] Backups configured
- [ ] Security groups configured
- [ ] Logs being collected
- [ ] Health checks working

## 🔗 **Useful Commands**

```bash
# Check system status
/home/ubuntu/monitor.sh

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update application
cd /home/ubuntu/stock-ai && git pull && ./deploy.sh

# Check SSL certificate
sudo certbot certificates

# Backup database
/home/ubuntu/backup.sh
```

---

**Your application will be available at:**
- **Frontend**: https://stock-satta.online
- **Backend API**: https://stock-satta.online/api
- **API Docs**: https://stock-satta.online/docs

**Support:**
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Monitor system: `/home/ubuntu/monitor.sh`
- Backup data: `/home/ubuntu/backup.sh` 