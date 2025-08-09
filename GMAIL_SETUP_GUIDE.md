# Gmail Setup Guide for Stock AI

## 🎯 **Why Gmail?**
- ✅ **Free forever**
- ✅ **Reliable delivery**
- ✅ **Easy setup**
- ✅ **Professional appearance**
- ✅ **Good spam filtering**

## 📧 **Your Email Strategy:**
- **`noreply@stock-satta.online`** - For OTP emails (no replies)
- **`support@stock-satta.online`** - For user support (with replies)

## 🔧 **Step-by-Step Setup:**

### **Step 1: Create Gmail Account**
1. Go to [gmail.com](https://gmail.com)
2. Create a new Gmail account (e.g., `stockai.app@gmail.com`)
3. Verify your account

### **Step 2: Enable 2-Factor Authentication**
1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security**
3. Enable **2-Step Verification**
4. Add your phone number

### **Step 3: Generate App Password**
1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Select **Mail** as the app
3. Select **Other (Custom name)** as device
4. Enter name: **"StockAI SMTP"**
5. Click **Generate**
6. **Copy the 16-character password** (you'll only see it once!)

### **Step 4: Update Your .env File**
```bash
# Email Configuration - Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=stockai.app@gmail.com
SMTP_PASSWORD=your_16_character_app_password
SMTP_TLS=true
SMTP_SSL=false
FROM_EMAIL=noreply@stock-satta.online
FROM_NAME=StockAI
```

### **Step 5: Test the Setup**
```bash
python3 simple_email_test.py
```

## 📋 **Complete .env Configuration:**

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost/stock_ai

# JWT
JWT_SECRET=your_jwt_secret_here

# Redis
REDIS_URL=redis://localhost:6379

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Zerodha API
ZERODHA_API_KEY=your_zerodha_api_key
ZERODHA_API_SECRET=your_zerodha_api_secret

# Email Configuration - Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=stockai.app@gmail.com
SMTP_PASSWORD=your_16_character_app_password
SMTP_TLS=true
SMTP_SSL=false
FROM_EMAIL=noreply@stock-satta.online
FROM_NAME=StockAI

# Frontend URL
FRONTEND_URL=http://localhost:3000

# OTP Settings
OTP_EXPIRE_MINUTES=10
```

## 🧪 **Test Your Setup:**

Run the test script:
```bash
python3 simple_email_test.py
```

You should see:
```
✅ Connected to SMTP server
✅ TLS enabled
✅ Authentication successful
✅ Email sent successfully!
```

## 🔍 **Troubleshooting:**

### **If Authentication Fails:**
1. **Check App Password**: Make sure you're using the 16-character app password
2. **Enable 2FA**: You must have 2FA enabled to use app passwords
3. **Check Username**: Use the full Gmail address

### **If Connection Fails:**
1. **Check SMTP Host**: Should be `smtp.gmail.com`
2. **Check Port**: Should be `587`
3. **Check TLS**: Should be `true`

### **If Emails Go to Spam:**
1. **Add SPF Record**: Add to your DNS
2. **Add DKIM**: For better deliverability
3. **Warm up the account**: Send a few emails manually first

## 📈 **Scaling to Paid Services:**

### **When to Upgrade:**
- **100+ emails/day** → Consider SendGrid
- **1000+ emails/day** → Consider AWS SES
- **High volume** → Consider dedicated email service

### **Migration Path:**
1. **Start with Gmail** (free, reliable)
2. **Monitor usage** (check email logs)
3. **Upgrade when needed** (based on volume)

## 🎉 **Benefits of This Setup:**

✅ **Free forever**  
✅ **Reliable delivery**  
✅ **Easy to set up**  
✅ **Professional appearance**  
✅ **Good spam filtering**  
✅ **Easy to migrate later**  

---

**This is the perfect solution for your current needs!** 🚀 