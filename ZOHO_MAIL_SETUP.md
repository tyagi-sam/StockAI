# Zoho Mail Setup Guide for Stock AI

This guide will help you set up Zoho Mail for professional email communication in your Stock AI application.

## 🚀 Quick Setup Steps

### Step 1: Sign Up for Zoho Mail

1. **Visit Zoho Mail**: https://mail.zoho.com/
2. **Click "Get Started"**
3. **Choose your plan**:
   - **Free Plan**: 5 users, 5GB storage (Perfect for starting)
   - **Paid Plan**: $1/user/month, 10GB storage
4. **Enter your domain** (e.g., `stockai.com`)
5. **Create your account**

### Step 2: Domain Configuration

#### Option A: You already own a domain

1. **Add your domain** to Zoho Mail
2. **Verify domain ownership**:
   - Go to your domain registrar (GoDaddy, Namecheap, etc.)
   - Add the verification TXT record provided by Zoho
   - Wait for DNS propagation (usually 24-48 hours)

3. **Configure DNS records**:
   ```
   MX Record: yourdomain.com → mx.zoho.com (Priority: 10)
   TXT Record: yourdomain.com → v=spf1 include:zoho.com ~all
   CNAME Record: mail.yourdomain.com → smtp.zoho.com
   ```

#### Option B: Purchase a domain through Zoho

1. **Buy domain** during Zoho Mail signup
2. **DNS will be configured automatically**
3. **Wait for propagation** (24-48 hours)

### Step 3: Create Business Email

1. **Log into Zoho Mail admin panel**
2. **Navigate to "User Management"**
3. **Click "Add User"**
4. **Fill in details**:
   - **Email Address**: `noreply@yourdomain.com`
   - **Display Name**: StockAI
   - **Password**: Create a strong password
   - **Storage**: 5GB (free plan) or 10GB (paid plan)
5. **Click "Add User"**

### Step 4: Configure SMTP Settings

Update your `.env` file with these Zoho Mail settings:

```bash
# Email Configuration - Zoho Mail
SMTP_HOST=smtp.zoho.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=your_zoho_email_password
SMTP_TLS=true
SMTP_SSL=false
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=StockAI
```

### Step 5: Test Email Configuration

#### Test with Docker (Production)
```bash
# Test email sending
docker-compose -f docker-compose.prod.yml exec backend python -c "
import asyncio
from app.services.email import email_service

async def test_email():
    try:
        await email_service.send_email(
            to_email='test@example.com',
            subject='Stock AI - Email Test',
            body='This is a test email from Stock AI application.'
        )
        print('✅ Email sent successfully!')
    except Exception as e:
        print(f'❌ Email failed: {e}')

asyncio.run(test_email())
"
```

#### Test with Local Development
```bash
# Test email sending locally
cd backend
python -c "
import asyncio
import sys
sys.path.append('.')
from app.services.email import email_service

async def test_email():
    try:
        await email_service.send_email(
            to_email='test@example.com',
            subject='Stock AI - Email Test',
            body='This is a test email from Stock AI application.'
        )
        print('✅ Email sent successfully!')
    except Exception as e:
        print(f'❌ Email failed: {e}')

asyncio.run(test_email())
"
```

## 🔧 Advanced Configuration

### Email Templates

Zoho Mail supports email templates. You can create templates for:
- **Welcome emails**
- **OTP verification emails**
- **Password reset emails**
- **Account confirmation emails**

### Email Authentication

For better deliverability, set up:
1. **SPF Record**: Already configured in DNS
2. **DKIM**: Configure in Zoho Mail admin panel
3. **DMARC**: Add DMARC record to DNS

### Email Forwarding

Set up email forwarding for support:
1. **Create support@yourdomain.com**
2. **Forward to your main email**
3. **Configure auto-replies**

## 📧 Email Types in Stock AI

Your Stock AI application sends these types of emails:

### 1. OTP Verification Emails
```python
# Sent when users register or request OTP
Subject: "Verify your email - Stock AI"
Body: "Your OTP is: 123456"
```

### 2. Welcome Emails
```python
# Sent after successful registration
Subject: "Welcome to Stock AI!"
Body: "Thank you for joining Stock AI..."
```

### 3. Password Reset Emails
```python
# Sent when users request password reset
Subject: "Reset your password - Stock AI"
Body: "Click here to reset your password..."
```

## 🎯 Best Practices

### 1. Email Security
- ✅ Use strong passwords for email accounts
- ✅ Enable 2FA on Zoho Mail
- ✅ Regularly monitor email logs
- ✅ Set up email backup

### 2. Deliverability
- ✅ Warm up your domain gradually
- ✅ Monitor bounce rates
- ✅ Use consistent "From" addresses
- ✅ Include unsubscribe links

### 3. Monitoring
- ✅ Check email logs regularly
- ✅ Monitor delivery rates
- ✅ Set up alerts for failures
- ✅ Track email engagement

## 🚨 Troubleshooting

### Common Issues

#### 1. Email Not Sending
```bash
# Check SMTP settings
echo "Testing SMTP connection..."
telnet smtp.zoho.com 587

# Check environment variables
docker-compose -f docker-compose.prod.yml exec backend env | grep SMTP
```

#### 2. Authentication Failed
```bash
# Verify credentials
# 1. Check username/password in .env
# 2. Ensure account is not suspended
# 3. Check if 2FA is enabled (use app password)
```

#### 3. Domain Not Verified
```bash
# Check DNS records
dig MX yourdomain.com
dig TXT yourdomain.com

# Wait for DNS propagation
# DNS changes can take 24-48 hours
```

#### 4. Emails Going to Spam
```bash
# Check SPF record
dig TXT yourdomain.com

# Set up DKIM in Zoho admin panel
# Add DMARC record to DNS
```

### Debug Commands

#### Test SMTP Connection
```bash
# Test SMTP connection manually
openssl s_client -connect smtp.zoho.com:587 -starttls smtp
```

#### Check Email Logs
```bash
# View email service logs
docker-compose -f docker-compose.prod.yml logs backend | grep -i email
```

#### Verify Environment Variables
```bash
# Check if email variables are set correctly
docker-compose -f docker-compose.prod.yml exec backend env | grep -E "(SMTP|FROM)"
```

## 📊 Monitoring & Analytics

### Zoho Mail Analytics
- **Delivery rates**: Monitor in Zoho admin panel
- **Bounce rates**: Check regularly
- **Spam complaints**: Monitor and address
- **Open rates**: Track email engagement

### Application Monitoring
```bash
# Monitor email sending in your app
docker-compose -f docker-compose.prod.yml logs -f backend | grep -i email
```

## 🔄 Migration from Gmail

If you're currently using Gmail:

1. **Set up Zoho Mail** (follow steps above)
2. **Update environment variables** in `.env`
3. **Test email functionality**
4. **Update DNS records**
5. **Monitor for 24-48 hours**
6. **Remove old Gmail configuration**

## 💰 Cost Optimization

### Free Plan (Recommended for starting)
- ✅ 5 users included
- ✅ 5GB storage per user
- ✅ Professional domain email
- ✅ SMTP access
- ✅ Webmail interface

### Paid Plan ($1/user/month)
- ✅ 10GB storage per user
- ✅ Advanced features
- ✅ Better support
- ✅ More users

## 🎯 Next Steps

1. **Complete Zoho Mail setup**
2. **Test email functionality**
3. **Deploy to production**
4. **Monitor email delivery**
5. **Set up email templates**
6. **Configure monitoring alerts**

---

**Need Help?**
- Zoho Mail Support: https://help.zoho.com/
- DNS Configuration Help: Contact your domain registrar
- Application Integration: Check the logs and test commands above 