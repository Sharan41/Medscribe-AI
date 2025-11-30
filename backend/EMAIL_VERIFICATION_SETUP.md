# Email Verification Setup

## Current Issue

Login requires email verification. You have two options:

---

## Option 1: Disable Email Verification (For Testing)

**Recommended for development/testing**

1. **Go to Supabase Dashboard:**
   - Visit: https://supabase.com/dashboard
   - Select your project: `xgbimokjjgkzyyeiguoi`

2. **Disable Email Confirmation:**
   - Go to: **Authentication** → **Settings**
   - Scroll to **Email Auth**
   - **Uncheck:** "Enable email confirmations"
   - Click **Save**

3. **Test Login Again:**
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "smoggysai555@gmail.com", "password": "string"}'
   ```

**Result:** Login will work immediately without email verification.

---

## Option 2: Verify Email (For Production)

**Recommended for production**

1. **Check Your Email:**
   - Check inbox for: `smoggysai555@gmail.com`
   - Look for email from Supabase
   - Click verification link

2. **Then Login:**
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "smoggysai555@gmail.com", "password": "string"}'
   ```

**Result:** Login will work after email verification.

---

## Quick Fix (Recommended)

**For development, disable email verification:**

1. Supabase Dashboard → Authentication → Settings
2. Uncheck "Enable email confirmations"
3. Save
4. Test login again

**This allows immediate testing without email verification!**

---

## After Fixing

Once email verification is disabled, you can:
- ✅ Register users
- ✅ Login immediately
- ✅ Get JWT tokens
- ✅ Access protected endpoints
- ✅ Test full authentication flow

---

**Choose Option 1 for quick testing!** 🚀

