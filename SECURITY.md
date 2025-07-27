# Security Documentation

## Overview
This document outlines the security measures implemented in the StockAI application and provides guidelines for maintaining security.

## Security Features

### 1. Environment Variables Protection
- All sensitive configuration is stored in environment variables
- `.env` files are excluded from version control via `.gitignore`
- Environment variables are validated at startup
- Required fields are enforced with proper error handling

### 2. Authentication & Authorization
- JWT-based authentication with secure token generation
- Token expiration (24 hours by default)
- Secure password hashing using bcrypt
- **Secure OTP hashing using SHA256 with salt** ✅
- OAuth2 integration with Google for enhanced security
- WebSocket authentication with token validation

### 3. API Security
- CORS protection with configurable origins
- Trusted host middleware for production
- Input validation using Pydantic models
- SQL injection prevention through ORM usage
- Rate limiting considerations (to be implemented)

### 4. Data Protection
- Fernet encryption for sensitive data
- Secure database connections
- Redis password protection
- **Hashed OTP storage in Redis** ✅
- HTTPS enforcement in production

## Security Checklist

### ✅ Implemented
- [x] Environment variables for all secrets
- [x] JWT token authentication
- [x] Password hashing
- [x] **OTP hashing with salt** ✅
- [x] CORS protection
- [x] Input validation
- [x] SQL injection prevention
- [x] Secure headers
- [x] Token expiration
- [x] Error handling without information leakage

### ⚠️ Recommended Improvements
- [ ] Rate limiting implementation
- [ ] HTTPS enforcement in production
- [ ] Security headers (HSTS, CSP, etc.)
- [ ] API key rotation mechanism
- [ ] Audit logging
- [ ] Penetration testing
- [ ] Dependency vulnerability scanning

## OTP Security Implementation

### How OTPs are Secured
1. **Generation**: Random 6-digit OTP using `secrets` module
2. **Hashing**: SHA256 hash with unique salt per OTP
3. **Storage**: Only hashed OTP and salt stored in Redis
4. **Verification**: Hash provided OTP with stored salt and compare
5. **Expiration**: Automatic deletion after 10 minutes
6. **Rate Limiting**: Maximum 5 attempts per OTP

### Security Benefits
- ✅ **One-way hashing**: Cannot reverse to original OTP
- ✅ **Salt protection**: Prevents rainbow table attacks
- ✅ **Unique salt per OTP**: Each OTP has different salt
- ✅ **Temporary storage**: Redis with automatic expiration
- ✅ **Attempt limiting**: Prevents brute force attacks

### Code Example
```python
# OTP Generation and Storage
otp = "123456"  # Generated OTP
salt = secrets.token_hex(16)  # Unique salt
otp_hash = hashlib.sha256((otp + salt).encode()).hexdigest()

# Storage in Redis
otp_data = {
    "otp_hash": otp_hash,  # Never store plain OTP
    "salt": salt,
    "created_at": datetime.utcnow().isoformat(),
    "attempts": 0
}

# Verification
provided_otp_hash = hashlib.sha256((provided_otp + salt).encode()).hexdigest()
is_valid = provided_otp_hash == stored_otp_hash
```

## Environment Variables Security

### Required Variables
```bash
# Security
JWT_SECRET=<32+ character secret>
FERNET_KEY=<base64-encoded 32-byte key>

# Database
DATABASE_URL=<postgresql://user:pass@host:port/db>
POSTGRES_PASSWORD=<database password>

# Redis
REDIS_URL=<redis://host:port>
REDIS_PASSWORD=<redis password>

# OAuth
GOOGLE_CLIENT_ID=<google oauth client id>
GOOGLE_CLIENT_SECRET=<google oauth client secret>

# API Keys
ZERODHA_API_KEY=<zerodha api key>
ZERODHA_API_SECRET=<zerodha api secret>
OPENAI_API_KEY=<openai api key>

# OTP Configuration
OTP_EXPIRE_MINUTES=10
OTP_LENGTH=6
```

### Security Best Practices
1. **Never commit `.env` files to version control**
2. **Use strong, unique secrets for each environment**
3. **Rotate secrets regularly**
4. **Use different secrets for development and production**
5. **Limit access to production secrets**

## API Security

### Authentication Flow
1. User submits credentials via `/auth/login`
2. Server validates credentials and returns JWT token
3. Client includes token in `Authorization: Bearer <token>` header
4. Server validates token on each request
5. Token expires after configured time (24 hours default)

### OTP Verification Flow
1. User registers with email/password
2. Server generates random OTP and hashes it with salt
3. Hashed OTP and salt stored in Redis with expiration
4. User receives plain OTP via email
5. User submits OTP for verification
6. Server hashes provided OTP with stored salt and compares
7. OTP deleted from Redis after successful verification

### CORS Configuration
```python
# Development
BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:3001"

# Production
BACKEND_CORS_ORIGINS="https://yourdomain.com"
```

## Database Security

### PostgreSQL Security
- Use strong passwords
- Enable SSL connections
- Limit database access to application servers
- Regular backups with encryption
- Monitor for suspicious activity

### Redis Security
- Use authentication
- Bind to localhost only
- Disable dangerous commands
- Use SSL in production
- **Hashed OTP storage** ✅

## Frontend Security

### Client-Side Security
- No sensitive data stored in localStorage (except JWT tokens)
- API calls use HTTPS
- Input validation on client and server
- XSS prevention through proper escaping

### Environment Variables
- Only `NEXT_PUBLIC_*` variables are exposed to client
- Sensitive variables remain server-side only

## Deployment Security

### Production Checklist
- [ ] Use HTTPS only
- [ ] Configure proper CORS origins
- [ ] Set up firewall rules
- [ ] Enable security headers
- [ ] Use strong secrets
- [ ] Monitor logs for suspicious activity
- [ ] Regular security updates
- [ ] **Verify OTP hashing is enabled** ✅

## Monitoring & Logging

### Security Logging
- Authentication attempts (success/failure)
- API access patterns
- Error logs without sensitive data
- Database access monitoring

### Alerts
- Failed authentication attempts
- Unusual API usage patterns
- Database connection issues
- SSL certificate expiration

## Incident Response

### Security Breach Response
1. **Immediate Actions**
   - Isolate affected systems
   - Preserve evidence
   - Assess scope of breach

2. **Communication**
   - Notify stakeholders
   - Document incident
   - Plan remediation

3. **Recovery**
   - Rotate all secrets
   - Update security measures
   - Monitor for recurrence

## Security Testing

### Regular Security Checks
- [ ] Dependency vulnerability scanning
- [ ] Penetration testing
- [ ] Code security review
- [ ] Infrastructure security audit
- [ ] API security testing

### Tools
- `npm audit` for Node.js dependencies
- `safety` for Python dependencies
- OWASP ZAP for penetration testing
- SonarQube for code analysis

## Compliance

### Data Protection
- Follow GDPR principles for user data
- Implement data retention policies
- Provide data export/deletion capabilities
- Document data processing activities

### Privacy
- Minimize data collection
- Encrypt data at rest and in transit
- Implement access controls
- Regular privacy impact assessments

## Contact

For security issues, please contact the development team immediately.
Do not disclose security issues publicly until they are resolved.

---

**Last Updated**: December 2024
**Version**: 1.0 