# Security Architecture: MedScribe AI

**Document Type:** Security Design Specification  
**Project:** MedScribe AI  
**Version:** 1.0  
**Date:** November 29, 2024

---

## 🔒 Security Overview

**Compliance Requirements:**
- DPDP Act (Digital Personal Data Protection Act, 2023)
- Medical Records Retention (7 years)
- Data Encryption (at rest and in transit)
- Audit Logging

**Security Principles:**
- Defense in depth
- Least privilege
- Zero trust
- Encryption everywhere

---

## 🔐 Authentication & Authorization

### Authentication Flow

```
User Login
    │
    ├─> POST /auth/login
    │   ├─> Email + Password
    │   │
    │   ├─> Validate Credentials
    │   │   ├─> Check Email exists
    │   │   ├─> Verify Password (bcrypt.compare)
    │   │   └─> Check Account Active
    │   │
    │   ├─> Generate JWT Token
    │   │   ├─> Payload: {user_id, email, exp, iat}
    │   │   ├─> Secret: Environment Variable (256-bit)
    │   │   ├─> Algorithm: HS256
    │   │   └─> Expiry: 24 hours
    │   │
    │   ├─> Generate Refresh Token
    │   │   ├─> Random UUID
    │   │   ├─> Store in Database (hashed)
    │   │   └─> Expiry: 7 days
    │   │
    │   └─> Return Tokens
    │
    └─> Store Tokens (Frontend)
        ├─> Access Token: Memory (recommended) or HttpOnly Cookie
        └─> Refresh Token: HttpOnly Cookie (secure, httpOnly, sameSite)
```

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "uuid",
    "email": "priya@clinic.com",
    "exp": 1638288000,
    "iat": 1638201600,
    "type": "access"
  },
  "signature": "HMACSHA256(...)"
}
```

### Authorization (RBAC)

**Roles:**
- `doctor`: Full access to own notes
- `admin`: Access to all notes (future)
- `readonly`: Read-only access (future)

**Permission Checks:**
```python
# Example: Check if user can access note
def can_access_note(user_id: str, note_user_id: str) -> bool:
    return user_id == note_user_id  # Doctors can only access own notes
```

---

## 🔒 Data Encryption

### Encryption at Rest

**PostgreSQL:**
```sql
-- Encrypt sensitive fields
-- Using pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt patient names
UPDATE consultations 
SET patient_name = pgp_sym_encrypt(patient_name, 'encryption_key');

-- Decrypt when reading
SELECT pgp_sym_decrypt(patient_name, 'encryption_key') 
FROM consultations;
```

**MongoDB:**
```python
# Field-level encryption
from cryptography.fernet import Fernet

key = os.getenv("ENCRYPTION_KEY")
cipher = Fernet(key)

# Encrypt before storing
encrypted_patient_name = cipher.encrypt(patient_name.encode())

# Decrypt when reading
decrypted_patient_name = cipher.decrypt(encrypted_patient_name).decode()
```

**File Storage (S3):**
- Server-side encryption (SSE-S3)
- Encryption key: Managed by AWS
- All audio files encrypted

### Encryption in Transit

**TLS Configuration:**
- **Version:** TLS 1.3 (minimum TLS 1.2)
- **Ciphers:** Strong ciphers only
- **Certificate:** Valid SSL certificate (Let's Encrypt)
- **HSTS:** Enabled (Strict-Transport-Security)

**API Calls:**
- All API endpoints: HTTPS only
- Database connections: SSL/TLS
- External API calls: HTTPS

---

## 🛡️ API Security

### Rate Limiting

**Implementation:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/notes/generate")
@limiter.limit("200/hour")
async def generate_note(request: Request):
    ...
```

**Limits:**
- Authentication: 10/minute
- Audio Upload: 20/hour
- Transcription: 100/hour
- SOAP Generation: 200/hour
- General API: 1000/hour

### Input Validation

**Pydantic Models:**
```python
from pydantic import BaseModel, EmailStr, validator

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
```

### SQL Injection Prevention

**Parameterized Queries:**
```python
# ✅ Safe
query = "SELECT * FROM users WHERE email = :email"
result = db.execute(query, {"email": user_email})

# ❌ Never do this
query = f"SELECT * FROM users WHERE email = '{user_email}'"
```

### XSS Prevention

**Frontend:**
- React automatically escapes content
- Use `dangerouslySetInnerHTML` only when necessary
- Sanitize user input

**Backend:**
- Validate and sanitize all inputs
- Return JSON (not HTML)
- Set Content-Type headers correctly

---

## 🔍 Audit Logging

### What to Log

**User Actions:**
- Login/logout
- Note creation
- Note updates
- Note deletion
- Profile changes

**System Events:**
- API failures
- Authentication failures
- Rate limit violations
- External API errors

**Log Format:**
```json
{
  "timestamp": "2024-11-29T10:00:00Z",
  "user_id": "uuid",
  "action": "create",
  "resource_type": "note",
  "resource_id": "uuid",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "success": true,
  "details": {}
}
```

### Log Retention

- **Retention Period:** 7 years (medical records)
- **Storage:** PostgreSQL audit_logs table
- **Backup:** Daily backups
- **Access:** Admin only, encrypted

---

## 🔐 DPDP Compliance

### Data Protection Requirements

**1. Consent Management:**
```python
class Consent(BaseModel):
    user_id: str
    consent_type: str  # "recording", "data_processing", "data_storage"
    granted: bool
    granted_at: datetime
    expires_at: datetime  # Optional
```

**2. Right to Access:**
- Users can request all their data
- Export in JSON/PDF format
- Response time: 30 days

**3. Right to Deletion:**
- Users can request data deletion
- Soft delete first (30 days grace)
- Hard delete after grace period
- Audit logs retained (legal requirement)

**4. Data Minimization:**
- Collect only necessary data
- Don't store unnecessary information
- Regular data cleanup

**5. Purpose Limitation:**
- Use data only for stated purpose
- No sharing without consent
- Clear privacy policy

---

## 🚨 Security Monitoring

### Monitoring Tools

**Application Monitoring:**
- Sentry: Error tracking
- CloudWatch: Logs and metrics
- Custom alerts: Security events

**Security Events to Monitor:**
- Failed login attempts (>5 in 5 min)
- Unusual API usage patterns
- Data access from new IP
- Large data exports
- Multiple note deletions

### Alert Thresholds

```python
# Example alert conditions
ALERTS = {
    "failed_logins": {
        "threshold": 5,
        "window": "5 minutes",
        "action": "lock_account"
    },
    "api_errors": {
        "threshold": 100,
        "window": "1 hour",
        "action": "notify_admin"
    },
    "data_export": {
        "threshold": 10,
        "window": "1 hour",
        "action": "review_access"
    }
}
```

---

## 🔄 Security Best Practices

### Password Security

**Requirements:**
- Minimum 8 characters
- At least 1 uppercase
- At least 1 lowercase
- At least 1 digit
- At least 1 special character

**Storage:**
- Hash with bcrypt (cost factor: 12)
- Never store plain text
- Salt included in hash

**Reset:**
- Token expires in 1 hour
- One-time use only
- Secure token generation

### API Key Management

**Storage:**
- Environment variables (never in code)
- Secret management service (AWS Secrets Manager)
- Rotation: Every 90 days

**Access:**
- Least privilege principle
- Separate keys per environment
- Revoke immediately if compromised

### Session Management

**JWT Tokens:**
- Short expiry (24 hours)
- Refresh tokens (7 days)
- Token revocation list (Redis)

**Session Security:**
- HttpOnly cookies
- Secure flag (HTTPS only)
- SameSite: Strict

---

## 🛡️ Infrastructure Security

### Server Security

**OS Level:**
- Regular security updates
- Firewall rules (only necessary ports)
- SSH key authentication only
- Disable root login

**Application Level:**
- Run as non-root user
- Minimal permissions
- Container security (if using Docker)

### Network Security

**Firewall Rules:**
- Allow: 443 (HTTPS), 80 (HTTP redirect)
- Deny: All other ports
- VPN for admin access

**DDoS Protection:**
- Rate limiting
- CloudFlare or AWS Shield
- IP blocking for abuse

---

## 🔐 Data Backup Security

### Backup Encryption

- All backups encrypted (AES-256)
- Encryption keys: Separate from data
- Key rotation: Every 90 days

### Backup Access

- Encrypted storage (S3 with encryption)
- Access logs for all backup operations
- Regular restore testing

---

## ✅ Security Checklist

### Pre-Launch

- [ ] All endpoints use HTTPS
- [ ] JWT tokens properly configured
- [ ] Password hashing implemented (bcrypt)
- [ ] Input validation on all endpoints
- [ ] Rate limiting enabled
- [ ] Audit logging implemented
- [ ] Encryption at rest enabled
- [ ] DPDP compliance measures in place
- [ ] Security headers configured
- [ ] Error messages don't leak information
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified
- [ ] CORS properly configured
- [ ] API keys stored securely
- [ ] Backup encryption enabled

### Post-Launch

- [ ] Security monitoring active
- [ ] Regular security audits
- [ ] Penetration testing (quarterly)
- [ ] Dependency updates (weekly)
- [ ] Security incident response plan
- [ ] Regular backup testing

---

## 🚨 Incident Response Plan

### Security Incident Types

1. **Data Breach:**
   - Immediate: Isolate affected systems
   - Notify: Users within 72 hours (DPDP requirement)
   - Investigate: Root cause analysis
   - Remediate: Fix vulnerabilities

2. **API Abuse:**
   - Immediate: Block IP addresses
   - Review: Access logs
   - Enhance: Rate limiting

3. **Account Compromise:**
   - Immediate: Lock account
   - Notify: User
   - Reset: All sessions
   - Review: Access logs

---

## 📚 Security References

- DPDP Act: https://amlegals.com/health-data-and-the-dpdp-act-a-practical-guide/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- JWT Best Practices: https://jwt.io/introduction

---

## ✅ Next Steps

1. **Integration Design** - External API security
2. **Implementation** - Code security measures
3. **Testing** - Security testing plan

---

**Document Status:** ✅ Complete  
**Ready for:** Integration Design  
**Next Document:** `integration-design.md`

---

**Last Updated:** November 29, 2024  
**Version:** 1.0

