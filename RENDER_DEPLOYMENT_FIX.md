# 🔧 Render Deployment Fix Guide

## Current Issue

Both backend and frontend deployments are failing. Here's how to fix them:

## Backend Deployment Fix

### Issue 1: Root Directory Path

The `startCommand` should NOT include `cd backend` because Render already sets the working directory to `rootDir`.

**Fixed render.yaml:**
```yaml
- type: web
  name: medscribe-backend
  runtime: python
  plan: free
  rootDir: backend
  buildCommand: pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
  startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  healthCheckPath: /health
```

### Issue 2: Missing Environment Variables

**CRITICAL:** You must set these environment variables in Render dashboard BEFORE deployment:

1. Go to your blueprint → Backend service → Environment
2. Add these variables:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
GEMINI_API_KEY=your_gemini_api_key
CORS_ORIGINS=https://medscribe-frontend.onrender.com
```

**Note:** You can set `CORS_ORIGINS` after frontend is deployed, but others are required.

### Issue 3: Python Version

Create `backend/runtime.txt`:
```
python-3.11.0
```

## Frontend Deployment Fix

### Issue 1: Build Command

The build command should handle TypeScript compilation:

**Current (should work):**
```yaml
buildCommand: npm install && npm run build
```

**If TypeScript errors occur, use:**
```yaml
buildCommand: npm ci && npm run build
```

### Issue 2: Environment Variables

Set these in Frontend service → Environment:

```env
VITE_API_URL=https://medscribe-backend.onrender.com
```

**Important:** 
- Wait until backend is deployed first
- Then update `VITE_API_URL` with actual backend URL
- Frontend will rebuild automatically

### Issue 3: Build Output

Verify `dist` folder is created. Check `frontend/vite.config.ts`:

```typescript
export default defineConfig({
  build: {
    outDir: 'dist', // Should be 'dist'
  }
})
```

## Step-by-Step Fix Process

### Step 1: Fix render.yaml

The file has been updated. Commit and push:

```bash
git add render.yaml backend/runtime.txt
git commit -m "Fix Render deployment configuration"
git push origin main
```

### Step 2: Manual Deployment (Recommended)

Instead of using Blueprint, deploy services manually:

#### Deploy Backend:

1. Go to Render Dashboard → "New +" → "Web Service"
2. Connect GitHub repo: `Sharan41/Medscribe-AI`
3. Settings:
   - **Name**: `medscribe-backend`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables** (Add these):
   ```
   SUPABASE_URL=your_url
   SUPABASE_KEY=your_key
   SUPABASE_SERVICE_KEY=your_service_key
   GEMINI_API_KEY=your_key
   CORS_ORIGINS=http://localhost:5173
   ```
5. Click "Create Web Service"
6. Wait for deployment (2-5 minutes)
7. Note the URL: `https://medscribe-backend.onrender.com`

#### Deploy Frontend:

1. Go to Render Dashboard → "New +" → "Static Site"
2. Connect GitHub repo: `Sharan41/Medscribe-AI`
3. Settings:
   - **Name**: `medscribe-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. **Environment Variables**:
   ```
   VITE_API_URL=https://medscribe-backend.onrender.com
   ```
   (Use the actual backend URL from step above)
5. Click "Create Static Site"
6. Wait for deployment (3-5 minutes)

### Step 3: Update CORS

After frontend is deployed:

1. Go to Backend service → Environment
2. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://medscribe-frontend.onrender.com,http://localhost:5173
   ```
3. Save (auto-redeploys)

## Troubleshooting

### Backend Fails: "Module not found"

**Solution:**
- Check `requirements.txt` includes all dependencies
- Verify build logs for missing packages
- Add missing packages to `requirements.txt`

### Backend Fails: "Port already in use"

**Solution:**
- Ensure start command uses `$PORT` variable
- Don't hardcode port numbers

### Frontend Fails: "Build failed"

**Check logs for:**
1. TypeScript errors → Fix TypeScript issues
2. Missing dependencies → Check `package.json`
3. Environment variable issues → Ensure `VITE_*` prefix

### Both Fail: Blueprint Issues

**Solution:**
- Deploy services manually instead of using Blueprint
- Blueprints can be finicky with complex setups

## Quick Checklist

- [ ] `render.yaml` updated and pushed
- [ ] `backend/runtime.txt` created
- [ ] Backend deployed manually
- [ ] Backend environment variables set
- [ ] Backend health check works (`/health`)
- [ ] Frontend deployed manually
- [ ] Frontend environment variables set
- [ ] CORS updated with frontend URL
- [ ] Test end-to-end flow

## Alternative: Use Render CLI

```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy from render.yaml
render deploy
```

---

**Next Steps:** Deploy manually first, then optimize with Blueprint later.

