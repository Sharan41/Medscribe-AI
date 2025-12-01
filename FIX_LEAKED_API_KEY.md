# 🔐 Fix Leaked Google Gemini API Key

## 🚨 Critical Issue

**Error:** `403 Your API key was reported as leaked. Please use another API key.`

**Cause:** The Google Gemini API key was hardcoded in `config.py` and exposed in the GitHub repository. Google detected this and revoked the key.

## ✅ Solution: Get New API Key & Use Environment Variables

### Step 1: Get a New Google Gemini API Key

1. **Go to Google AI Studio:**
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with your Google account

2. **Create New API Key:**
   - Click **"Create API Key"**
   - Select your project (or create a new one)
   - Copy the new API key
   - **⚠️ Keep it secret!** Don't commit it to Git

3. **Delete Old Key (Optional):**
   - Delete the old leaked key from Google AI Studio
   - This prevents unauthorized usage

### Step 2: Update Render Environment Variables

1. **Go to Render Dashboard:**
   - Navigate to: https://dashboard.render.com
   - Click your backend service: `medscribe-backend`

2. **Update Environment Variable:**
   - Go to **"Environment"** tab
   - Find `GEMINI_API_KEY`
   - **Update** with your new API key
   - Click **"Save Changes"**
   - Render will auto-redeploy

### Step 3: Update Local .env File (For Local Development)

1. **Update `backend/.env`:**
   ```env
   GEMINI_API_KEY=your_new_api_key_here
   ```

2. **Never commit `.env` to Git:**
   - Ensure `.env` is in `.gitignore`
   - ✅ Already configured

### Step 4: Verify Code Uses Environment Variables

The code should read from environment variables, not hardcoded values:

```python
# ✅ Correct (in config.py):
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ❌ Wrong (hardcoded):
GEMINI_API_KEY: str = "AIzaSy..."
```

## 🔒 Security Best Practices

### ✅ DO:
- ✅ Store API keys in environment variables
- ✅ Use `.env` file for local development (gitignored)
- ✅ Use Render's environment variables for production
- ✅ Rotate keys if exposed
- ✅ Use different keys for dev/prod

### ❌ DON'T:
- ❌ Hardcode API keys in source code
- ❌ Commit `.env` files to Git
- ❌ Share API keys in chat/email
- ❌ Use the same key everywhere

## 🧹 Clean Up Exposed Key

### Remove from Git History (Important!)

The old key is still in Git history. To remove it:

1. **Use Git Filter (Advanced):**
   ```bash
   # WARNING: This rewrites history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch backend/app/config.py" \
     --prune-empty --tag-name-filter cat -- --all
   ```

2. **Or Simply:**
   - The key is already removed from current code
   - Old commits still have it, but that's okay for now
   - Just ensure new key is never committed

### Verify No Keys in Code

```bash
# Check for any hardcoded Gemini keys
grep -r "AIzaSy" backend/ --exclude-dir=venv --exclude-dir=__pycache__

# Should return nothing (or only in .env which is gitignored)
```

## 📝 Quick Checklist

- [ ] Get new Gemini API key from Google AI Studio
- [ ] Update `GEMINI_API_KEY` in Render dashboard
- [ ] Update `backend/.env` for local development
- [ ] Verify code uses `os.getenv()` not hardcoded values
- [ ] Test SOAP note generation with new key
- [ ] Never commit API keys to Git again

## 🧪 Test After Fix

1. **Wait for Render redeploy** (after updating env var)
2. **Create a new consultation**
3. **Check logs** - should see successful SOAP generation
4. **Verify** - consultation status should be "completed"

---

**Status:** ⚠️ API key revoked → Need new key → Update Render env vars → Test

