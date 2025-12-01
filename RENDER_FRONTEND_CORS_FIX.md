# 🔧 Fix Frontend CORS Error on Render

## Problem

Frontend on Render is trying to connect to `http://localhost:8000` instead of the Render backend URL, causing CORS errors:

```
Access to XMLHttpRequest at 'http://localhost:8000/auth/register' from origin 'https://medscribe-frontend.onrender.com' 
has been blocked by CORS policy
```

## Root Cause

The `VITE_API_URL` environment variable is **not set** or **incorrect** in Render's frontend service configuration.

**Important:** Vite environment variables are baked into the build at **build time**, not runtime. If the variable isn't set during build, it falls back to `http://localhost:8000`.

## Solution

### Step 1: Set Environment Variable in Render

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Click on your **Frontend Static Site** service (`medscribe-ai-frontend`)

2. **Go to Environment Section**
   - Click on **"Environment"** in the left sidebar
   - Or go to **Settings** → **Environment**

3. **Add/Update Environment Variable**
   - Click **"+ Add Environment Variable"** (if not exists)
   - Or click **"Edit"** next to existing `VITE_API_URL`
   
   **Key:** `VITE_API_URL`
   
   **Value:** `https://medscribe-backend-63pu.onrender.com`
   
   ⚠️ **Important:** Use your actual backend URL from Render dashboard!

4. **Save Changes**
   - Click **"Save Changes"**
   - Render will automatically trigger a rebuild

### Step 2: Verify Backend CORS Configuration

Make sure your backend has the frontend URL in CORS origins:

1. **Go to Backend Service** → **Environment**
2. Check `CORS_ORIGINS` includes:
   ```
   https://medscribe-ai-frontend.onrender.com,http://localhost:5173
   ```
3. If not, add it and save (auto-redeploys)

### Step 3: Wait for Rebuild

- Frontend rebuild takes **3-5 minutes**
- Watch the **Logs** tab to see build progress
- Once complete, test the registration page

## Verification

After rebuild completes:

1. **Check Build Logs**
   - Look for: `VITE_API_URL=https://medscribe-backend-63pu.onrender.com`
   - Should see environment variable being used

2. **Test Registration**
   - Go to: `https://medscribe-ai-frontend.onrender.com/register`
   - Try registering a new account
   - Should connect to Render backend (not localhost)

3. **Check Browser Console**
   - Open DevTools → Network tab
   - Registration request should go to: `https://medscribe-backend-63pu.onrender.com/auth/register`
   - NOT `http://localhost:8000/auth/register`

## Current Configuration

**Frontend API Service** (`frontend/src/services/api.ts`):
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

This means:
- ✅ If `VITE_API_URL` is set → Uses that URL
- ❌ If not set → Falls back to `localhost:8000` (causes CORS error)

## Troubleshooting

### Still Getting CORS Errors?

1. **Verify Environment Variable**
   - Go to Frontend service → Environment
   - Confirm `VITE_API_URL` is set correctly
   - Value should be: `https://medscribe-backend-63pu.onrender.com` (no trailing slash)

2. **Check Build Logs**
   - Frontend service → Logs
   - Look for build output
   - Should see environment variables being used

3. **Force Rebuild**
   - Go to Frontend service → Manual Deploy
   - Click **"Clear build cache & deploy"**
   - This ensures fresh build with environment variables

4. **Verify Backend CORS**
   - Backend service → Environment
   - `CORS_ORIGINS` should include frontend URL
   - Format: `https://medscribe-ai-frontend.onrender.com,http://localhost:5173`

### Environment Variable Not Working?

**Common Issues:**
- ❌ Variable name wrong (must be `VITE_API_URL`, not `API_URL`)
- ❌ Missing `VITE_` prefix (Vite only exposes variables starting with `VITE_`)
- ❌ Value has trailing slash (remove it: `https://backend.onrender.com/` → `https://backend.onrender.com`)
- ❌ Build cache (clear cache and rebuild)

---

**Status:** ⏳ Waiting for environment variable to be set in Render dashboard
**Next Step:** Set `VITE_API_URL` in Render frontend service → Auto-rebuild → Test

