# Development & Deployment Workflow

This guide covers how to develop new features and deploy them to production efficiently.

## 🔄 **Development Workflow**

### **Local Development Process**

```bash
# 1. Create feature branch
git checkout -b feature/new-feature-name

# 2. Develop your feature
# - Make changes to code
# - Test locally
# - Commit frequently

# 3. Test locally
docker-compose up --build
# Test at http://localhost:3000

# 4. Commit and push
git add .
git commit -m "Add new feature: description"
git push origin feature/new-feature-name

# 5. Create Pull Request (optional)
# Go to GitHub and create PR for code review
```

### **Testing Before Deployment**

```bash
# Test locally with production settings
cp env.production.example .env
# Edit .env with test values
docker-compose -f docker-compose.prod.yml up --build

# Run tests (if you have them)
# python -m pytest
# npm test
```

## 🚀 **Deployment Strategies**

### **Strategy 1: Quick Deploy (Recommended for small changes)**

```bash
# 1. Commit your changes
git add .
git commit -m "Add new feature"
git push origin main

# 2. Deploy to production
ssh -i your-key.pem ubuntu@your-ec2-ip << 'EOF'
    cd /home/ubuntu/stock-ai
    git pull origin main
    ./deploy.sh
EOF
```

### **Strategy 2: Feature Branch Deployment**

```bash
# 1. Create and work on feature branch
git checkout -b feature/new-feature
# ... develop your feature ...
git push origin feature/new-feature

# 2. Deploy feature branch to test
ssh -i your-key.pem ubuntu@your-ec2-ip << 'EOF'
    cd /home/ubuntu/stock-ai
    git fetch origin
    git checkout feature/new-feature
    git pull origin feature/new-feature
    ./deploy.sh
EOF

# 3. Test on production
# Visit https://stock-satta.online

# 4. If everything works, merge to main
git checkout main
git merge feature/new-feature
git push origin main

# 5. Deploy main branch
ssh -i your-key.pem ubuntu@your-ec2-ip << 'EOF'
    cd /home/ubuntu/stock-ai
    git checkout main
    git pull origin main
    ./deploy.sh
EOF
```

### **Strategy 3: Blue-Green Deployment (For Zero Downtime)**

```bash
# 1. Deploy to staging environment
ssh -i your-key.pem ubuntu@your-ec2-ip << 'EOF'
    cd /home/ubuntu/stock-ai
    git pull origin main
    
    # Stop current containers
    docker-compose -f docker-compose.prod.yml down
    
    # Build new containers
    docker-compose -f docker-compose.prod.yml up -d --build
    
    # Health check
    sleep 10
    curl -f http://localhost/health || exit 1
    curl -f http://localhost:8000/health || exit 1
EOF
```

## 🔧 **Development Environment Setup**

### **Local Development**

```bash
# 1. Clone repository
git clone https://github.com/yourusername/stock-ai.git
cd stock-ai

# 2. Set up development environment
cp env.example .env
# Edit .env with development values

# 3. Start development servers
docker-compose up --build

# 4. Access your app
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### **Development with Hot Reload**

```bash
# For frontend development (React)
cd frontend-react
npm install
npm run dev

# For backend development (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 **Deployment Checklist**

### **Before Deploying**

- [ ] **Code Review**: All changes reviewed
- [ ] **Local Testing**: Feature works locally
- [ ] **Environment Variables**: Updated if needed
- [ ] **Database Migrations**: Applied if needed
- [ ] **Dependencies**: Updated if needed
- [ ] **Security**: No sensitive data in code

### **Deployment Steps**

```bash
# 1. Update local repository
git pull origin main

# 2. Test locally
docker-compose -f docker-compose.prod.yml up --build

# 3. Deploy to production
ssh -i your-key.pem ubuntu@your-ec2-ip << 'EOF'
    cd /home/ubuntu/stock-ai
    git pull origin main
    ./deploy.sh
EOF

# 4. Verify deployment
curl https://stock-satta.online/health
curl https://stock-satta.online/api/health
```

### **Post-Deployment Verification**

- [ ] **Frontend**: https://stock-satta.online loads correctly
- [ ] **Backend API**: https://stock-satta.online/api/health returns 200
- [ ] **Database**: Data is accessible
- [ ] **Email**: Test email sending
- [ ] **Logs**: No errors in application logs

## 🔄 **Common Development Scenarios**

### **Scenario 1: Adding New API Endpoint**

```bash
# 1. Create feature branch
git checkout -b feature/new-api-endpoint

# 2. Add endpoint in backend/app/api/endpoints/
# 3. Test locally
curl http://localhost:8000/api/v1/your-endpoint

# 4. Commit and deploy
git add .
git commit -m "Add new API endpoint"
git push origin feature/new-api-endpoint

# 5. Deploy to test
ssh -i your-key.pem ubuntu@your-ec2-ip << 'EOF'
    cd /home/ubuntu/stock-ai
    git checkout feature/new-api-endpoint
    git pull origin feature/new-api-endpoint
    ./deploy.sh
EOF

# 6. Test on production
curl https://stock-satta.online/api/v1/your-endpoint
```

### **Scenario 2: Updating Frontend UI**

```bash
# 1. Create feature branch
git checkout -b feature/ui-update

# 2. Make changes in frontend-react/src/
# 3. Test locally
npm run dev

# 4. Build and test production build
npm run build
npm run preview

# 5. Deploy
git add .
git commit -m "Update UI components"
git push origin feature/ui-update

# 6. Deploy to production
ssh -i your-key.pem ubuntu@your-ec2-ip << 'EOF'
    cd /home/ubuntu/stock-ai
    git checkout feature/ui-update
    git pull origin feature/ui-update
    ./deploy.sh
EOF
```

### **Scenario 3: Database Schema Changes**

```bash
# 1. Create migration
cd backend
alembic revision --autogenerate -m "Add new table"

# 2. Test migration locally
alembic upgrade head

# 3. Deploy with migration
ssh -i your-key.pem ubuntu@your-ec2-ip << 'EOF'
    cd /home/ubuntu/stock-ai
    git pull origin main
    docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
    ./deploy.sh
EOF
```

## 🚨 **Rollback Strategy**

### **Quick Rollback**

```bash
# If deployment fails, rollback to previous version
ssh -i your-key.pem ubuntu@your-ec2-ip << 'EOF'
    cd /home/ubuntu/stock-ai
    git checkout HEAD~1
    ./deploy.sh
EOF
```

### **Database Rollback**

```bash
# Rollback database migration
ssh -i your-key.pem ubuntu@your-ec2-ip << 'EOF'
    cd /home/ubuntu/stock-ai
    docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
EOF
```

## 📊 **Monitoring & Debugging**

### **Check Application Status**

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Check system status
/home/ubuntu/monitor.sh

# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### **Debug Common Issues**

```bash
# Check if domain is resolving
nslookup stock-satta.online

# Check SSL certificate
sudo certbot certificates

# Check nginx status
sudo systemctl status nginx

# Check Docker status
sudo systemctl status docker

# Check disk space
df -h

# Check memory usage
free -h
```

## 🔧 **Automation Scripts**

### **Quick Deploy Script**

Create `quick-deploy.sh`:
```bash
#!/bin/bash
# Quick deploy script
EC2_IP="your-ec2-ip"
KEY_FILE="your-key.pem"

echo "🚀 Quick Deploy to Production"

# Push changes
git push origin main

# Deploy to production
ssh -i $KEY_FILE ubuntu@$EC2_IP << 'EOF'
    cd /home/ubuntu/stock-ai
    git pull origin main
    ./deploy.sh
EOF

echo "✅ Deployment completed!"
```

### **Feature Deploy Script**

Create `deploy-feature.sh`:
```bash
#!/bin/bash
# Deploy feature branch
FEATURE_BRANCH=$1
EC2_IP="your-ec2-ip"
KEY_FILE="your-key.pem"

if [ -z "$FEATURE_BRANCH" ]; then
    echo "Usage: ./deploy-feature.sh <branch-name>"
    exit 1
fi

echo "🚀 Deploying feature branch: $FEATURE_BRANCH"

# Push feature branch
git push origin $FEATURE_BRANCH

# Deploy to production
ssh -i $KEY_FILE ubuntu@$EC2_IP << EOF
    cd /home/ubuntu/stock-ai
    git fetch origin
    git checkout $FEATURE_BRANCH
    git pull origin $FEATURE_BRANCH
    ./deploy.sh
EOF

echo "✅ Feature deployment completed!"
```

## 📈 **Best Practices**

### **Development Best Practices**

1. **Always work on feature branches**
2. **Test locally before deploying**
3. **Keep commits small and descriptive**
4. **Use meaningful commit messages**
5. **Review code before merging to main**

### **Deployment Best Practices**

1. **Deploy during low-traffic hours**
2. **Always have a rollback plan**
3. **Monitor logs after deployment**
4. **Test critical functionality after deployment**
5. **Keep backups before major changes**

### **Monitoring Best Practices**

1. **Set up alerts for critical issues**
2. **Monitor application performance**
3. **Track error rates**
4. **Monitor resource usage**
5. **Regular security updates**

## 🎯 **Quick Reference Commands**

```bash
# Local development
docker-compose up --build

# Deploy to production
ssh -i key.pem ubuntu@ec2-ip "cd stock-ai && git pull && ./deploy.sh"

# Check status
ssh -i key.pem ubuntu@ec2-ip "/home/ubuntu/monitor.sh"

# View logs
ssh -i key.pem ubuntu@ec2-ip "cd stock-ai && docker-compose -f docker-compose.prod.yml logs -f"

# Backup
ssh -i key.pem ubuntu@ec2-ip "/home/ubuntu/backup.sh"

# Update application
ssh -i key.pem ubuntu@ec2-ip "cd stock-ai && git pull origin main && ./deploy.sh"
```

---

**Remember**: Always test your changes locally before deploying to production, and have a rollback plan ready! 