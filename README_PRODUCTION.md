# Stock AI - Production Deployment Guide

This guide covers deploying the Stock AI application to production with Docker.

## 🚀 Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- Domain name (optional but recommended)
- SSL certificate (recommended for production)

### 2. Setup Environment
```bash
# Copy production environment template
cp env.production.example .env

# Edit with your production values
nano .env
```

### 3. Deploy
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run production deployment
./deploy.sh
```

## 📋 Production Checklist

### ✅ Environment Variables
- [ ] `JWT_SECRET` (32+ characters, random)
- [ ] `FERNET_KEY` (base64 encoded 32-byte key)
- [ ] `POSTGRES_PASSWORD` (strong password)
- [ ] `REDIS_PASSWORD` (strong password)
- [ ] `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- [ ] `ZERODHA_API_KEY` and `ZERODHA_API_SECRET`
- [ ] `FRONTEND_URL` (your domain)
- [ ] `BACKEND_CORS_ORIGINS` (your domain)
- [ ] Email configuration (SMTP settings)

### ✅ Security
- [ ] Strong passwords for all services
- [ ] SSL/TLS certificates configured
- [ ] Firewall rules set up
- [ ] Regular security updates
- [ ] Database backups configured

### ✅ Monitoring
- [ ] Health checks configured
- [ ] Log monitoring set up
- [ ] Error tracking configured
- [ ] Performance monitoring

## 🔧 Configuration

### Environment Variables

#### Required Variables
```bash
# Security
JWT_SECRET=your_very_long_random_secret_here
FERNET_KEY=your_base64_encoded_32_byte_key

# Database
POSTGRES_USER=stock_ai_user
POSTGRES_PASSWORD=your_strong_password

# Redis
REDIS_PASSWORD=your_strong_password

# APIs
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
ZERODHA_API_KEY=your_zerodha_api_key
ZERODHA_API_SECRET=your_zerodha_api_secret

# Domain
FRONTEND_URL=https://yourdomain.com
BACKEND_CORS_ORIGINS=https://yourdomain.com
```

#### Optional Variables
```bash
# AI Analysis
OPENAI_API_KEY=your_openai_api_key

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Generating Security Keys

#### JWT Secret
```bash
# Generate a random 32-character string
openssl rand -base64 32
```

#### Fernet Key
```python
# Run this Python script
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

## 🐳 Docker Commands

### Production Deployment
```bash
# Deploy to production
./deploy.sh

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update deployment
docker-compose -f docker-compose.prod.yml down
./deploy.sh
```

### Health Checks
```bash
# Frontend health
curl http://localhost/health

# Backend health
curl http://localhost:8000/health

# Database health
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U stock_ai_user

# Redis health
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a your_redis_password ping
```

## 🔒 Security Best Practices

### 1. Passwords
- Use strong, unique passwords for each service
- Store passwords securely (not in version control)
- Rotate passwords regularly

### 2. SSL/TLS
```bash
# Install Certbot for Let's Encrypt
sudo apt-get install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure nginx with SSL
# (See nginx configuration examples)
```

### 3. Firewall
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 4. Database Security
- Use strong passwords
- Limit database access
- Regular backups
- Monitor for suspicious activity

## 📊 Monitoring & Logging

### Health Monitoring
```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Backup Strategy
```bash
# Database backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U stock_ai_user stock_ai > backup.sql

# Volume backup
docker run --rm -v stock_ai_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

## 🔄 Updates & Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and deploy
./deploy.sh
```

### Database Migrations
```bash
# Run migrations manually if needed
docker-compose -f docker-compose.prod.yml exec backend python -m alembic upgrade head
```

### Log Rotation
```bash
# Configure log rotation in your system
sudo nano /etc/logrotate.d/stock-ai
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using the ports
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000

# Stop conflicting services
sudo systemctl stop nginx  # if nginx is running
```

#### 2. Database Connection Issues
```bash
# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test database connection
docker-compose -f docker-compose.prod.yml exec backend python -c "
import asyncpg
import asyncio
async def test():
    try:
        conn = await asyncpg.connect('postgresql://user:pass@postgres:5432/stock_ai')
        print('Connection successful')
        await conn.close()
    except Exception as e:
        print(f'Connection failed: {e}')
asyncio.run(test())
"
```

#### 3. Frontend Build Issues
```bash
# Check frontend build logs
docker-compose -f docker-compose.prod.yml logs frontend

# Rebuild frontend
docker-compose -f docker-compose.prod.yml build --no-cache frontend
```

#### 4. Memory Issues
```bash
# Check Docker resource usage
docker stats

# Increase Docker memory limit
# (In Docker Desktop settings)
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_searches_timestamp ON searches(timestamp);
```

#### 2. Redis Optimization
```bash
# Configure Redis for production
# Edit redis.conf for persistence and memory settings
```

#### 3. Nginx Optimization
```nginx
# Enable gzip compression
# Configure caching
# Set up rate limiting
```

## 📞 Support

### Getting Help
1. Check the logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify environment variables: `cat .env`
3. Test individual services
4. Check system resources: `docker stats`

### Emergency Procedures
```bash
# Emergency stop
docker-compose -f docker-compose.prod.yml down

# Emergency restart
docker-compose -f docker-compose.prod.yml up -d

# Rollback to previous version
git checkout HEAD~1
./deploy.sh
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          # Add your deployment commands here
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancers
- Scale database with read replicas
- Use Redis clusters for high availability

### Vertical Scaling
- Increase container resources
- Optimize database queries
- Use CDN for static assets

## 🎯 Production Checklist Summary

- [ ] Environment variables configured
- [ ] Security keys generated
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Monitoring set up
- [ ] Backups configured
- [ ] Health checks working
- [ ] Performance optimized
- [ ] Documentation updated
- [ ] Team trained on deployment

---

**Remember**: Production deployments require careful planning and testing. Always test in a staging environment first! 