# 🔧 Fix CORS Error on Render

## Issue

Frontend at `https://medscribe-ai-frontend.onrender.com` cannot access backend at `https://medscribe-backend-63pu.onrender.com` due to CORS policy.

**Error:**
```
Access to XMLHttpRequest at 'https://medscribe-backend-63pu.onrender.com/auth/login' 
from origin 'https://medscribe-ai-frontend.onrender.com' has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Solution

Update the `CORS_ORIGINS` environment variable in your Render backend service.

### Step 1: Go to Render Dashboard

1. Navigate to [Render Dashboard](https://dashboard.render.com)
2. Click on your **backend service**: `medscribe-backend`
3. Go to **Environment** tab

### Step 2: Update CORS_ORIGINS

Find the `CORS_ORIGINS` environment variable and update it to:

```
https://medscribe-ai-frontend.onrender.com,http://localhost:5173
```

**Or if you want to allow all origins (for testing only):**
```
*
```

**Important:** 
- Include your frontend URL: `https://medscribe-ai-frontend.onrender.com`
- Keep `http://localhost:5173` for local development
- Separate multiple origins with commas (no spaces)

### Step 3: Save and Redeploy

1. Click **"Save Changes"**
2. Render will automatically redeploy your backend
3. Wait 2-5 minutes for redeployment

### Step 4: Verify

After redeployment:
1. Check backend logs for successful start
2. Test frontend login again
3. CORS error should be resolved

## Alternative: Update via render.yaml

If you want to update via code, modify `render.yaml`:

```yaml
envVars:
  - key: CORS_ORIGINS
    value: https://medscribe-ai-frontend.onrender.com,http://localhost:5173
```

Then commit and push:
```bash
git add render.yaml
git commit -m "Update CORS_ORIGINS with frontend URL"
git push origin main
```

## Quick Fix (Temporary - Testing Only)

If you need immediate access for testing, you can temporarily allow all origins:

**In Render Dashboard → Backend → Environment:**
```
CORS_ORIGINS=*
```

**⚠️ Warning:** This allows any origin to access your API. Only use for testing!

## Verify Backend CORS Configuration

The backend code in `app/main.py` should have:

```python
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

This configuration is correct and will work once `CORS_ORIGINS` is set properly.

## Troubleshooting

### Still Getting CORS Errors?

1. **Check Environment Variable:**
   - Verify `CORS_ORIGINS` is set correctly in Render
   - No extra spaces or quotes
   - URLs match exactly (including `https://`)

2. **Check Backend Logs:**
   - Go to Backend → Logs
   - Look for CORS-related errors
   - Verify backend started successfully

3. **Test Backend Directly:**
   - Visit: `https://medscribe-backend-63pu.onrender.com/docs`
   - Should show FastAPI docs
   - If not accessible, backend might be down

4. **Clear Browser Cache:**
   - Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
   - Or clear browser cache

5. **Check Preflight Request:**
   - Open browser DevTools → Network tab
   - Look for OPTIONS request to `/auth/login`
   - Should return 200 OK with CORS headers

## Expected CORS Headers

After fixing, the response should include:
```
Access-Control-Allow-Origin: https://medscribe-ai-frontend.onrender.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: *
```

---

**Status:** Update `CORS_ORIGINS` in Render dashboard → Backend → Environment

