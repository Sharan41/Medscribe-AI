# Testing Guide - MedScribe AI Backend

## ⚠️ Important: Email Validation

**Supabase Auth validates email domains**, so you cannot use fake emails like `test@example.com`.

### Use Real Email Addresses for Testing

**Valid test emails:**
- Gmail: `yourname@gmail.com`
- Outlook: `yourname@outlook.com`
- Any real email service

**Invalid (will fail):**
- `test@example.com` ❌
- `test@test.com` ❌
- `fake@fake.com` ❌

---

## 🧪 Testing Registration

### Option 1: Use Swagger UI (Easiest)

1. Open: http://localhost:8000/docs
2. Find `POST /auth/register`
3. Click "Try it out"
4. Use a **real email address**:
   ```json
   {
     "email": "yourrealemail@gmail.com",
     "password": "Test123!",
     "name": "Dr. Test",
     "clinic_name": "Test Clinic"
   }
   ```
5. Click "Execute"

### Option 2: Use cURL

```bash
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "yourrealemail@gmail.com",
    "password": "Test123!",
    "name": "Dr. Test",
    "clinic_name": "Test Clinic"
  }'
```

**Replace `yourrealemail@gmail.com` with your real email!**

---

## 🔧 Supabase Email Settings

If you want to allow test emails in development:

1. Go to Supabase Dashboard
2. Authentication → Settings
3. Email Auth → Disable "Confirm email" (for testing)
4. Or add your test domain to allowed domains

---

## ✅ Expected Response

**Success (200):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "yourrealemail@gmail.com",
    "name": "Dr. Test"
  },
  "message": "Registration successful. Please verify your email.",
  "session": {
    "access_token": "...",
    "refresh_token": "..."
  }
}
```

**Error (400):**
```json
{
  "detail": "Email validation failed: ... Use a real email address for testing"
}
```

---

## 🚀 Quick Test Commands

### Test Health
```bash
curl http://localhost:8000/health
```

### Test Registration (with real email)
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "YOUR_REAL_EMAIL@gmail.com",
    "password": "Test123!",
    "name": "Dr. Test",
    "clinic_name": "Test Clinic"
  }'
```

---

**Remember:** Always use a real email address for testing! 📧

