# 🚀 Deploy MedScribe AI to Render

Complete guide to deploy MedScribe AI backend and frontend to Render.com.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Deployment Overview](#deployment-overview)
- [Step 1: Deploy Backend (FastAPI)](#step-1-deploy-backend-fastapi)
- [Step 2: Deploy Frontend (React)](#step-2-deploy-frontend-react)
- [Step 3: Configure Environment Variables](#step-3-configure-environment-variables)
- [Step 4: Database Setup](#step-4-database-setup)
- [Step 5: Test Deployment](#step-5-test-deployment)
- [Troubleshooting](#troubleshooting)

## ✅ Prerequisites

Before deploying, ensure you have:

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code pushed to GitHub (✅ Already done)
3. **Supabase Project**: Database and storage configured
4. **API Keys**:
   - Google Gemini API key
   - AssemblyAI API key (optional)
   - Reverie API key (optional)
   - Supabase credentials

## 🏗 Deployment Overview

MedScribe AI consists of two separate services:

1. **Backend Service** (FastAPI) - Web service
2. **Frontend Service** (React/Vite) - Static site

Both services will be deployed separately on Render.

---

## 📦 Step 1: Deploy Backend (FastAPI)

### 1.1 Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `Sharan41/Medscribe-AI`
4. Select the repository

### 1.2 Configure Backend Service

**Basic Settings:**
- **Name**: `medscribe-backend` (or your preferred name)
- **Region**: Choose closest to your users (e.g., `Singapore` for India)
- **Branch**: `main`
- **Root Directory**: `backend`

**Build & Deploy:**
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Advanced Settings:**
- **Auto-Deploy**: `Yes` (deploys on every push to main)
- **Health Check Path**: `/docs` (FastAPI docs endpoint)

### 1.3 Environment Variables (Backend)

Add these in the **Environment** section:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key

# AssemblyAI API (Optional)
ASSEMBLYAI_API_KEY=your_assemblyai_api_key

# Reverie API (Optional)
REVERIE_API_KEY=your_reverie_api_key
REVERIE_APP_ID=your_reverie_app_id

# CORS Configuration
CORS_ORIGINS=https://your-frontend-url.onrender.com,http://localhost:5173

# Server Configuration
PORT=10000
```

**Important Notes:**
- Replace `your-frontend-url.onrender.com` with your actual frontend URL (you'll get this after deploying frontend)
- Never commit `.env` files to Git
- Use Render's environment variables section for all secrets

### 1.4 Create `render.yaml` (Optional but Recommended)

Create `render.yaml` in the project root for infrastructure as code:

```yaml
services:
  - type: web
    name: medscribe-backend
    runtime: python
    plan: free  # or starter for production
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: ASSEMBLYAI_API_KEY
        sync: false
      - key: REVERIE_API_KEY
        sync: false
      - key: REVERIE_APP_ID
        sync: false
      - key: CORS_ORIGINS
        sync: false
```

### 1.5 Deploy Backend

1. Click **"Create Web Service"**
2. Render will start building and deploying
3. Wait for deployment to complete (usually 2-5 minutes)
4. Note your backend URL: `https://medscribe-backend.onrender.com`

---

## 🎨 Step 2: Deploy Frontend (React)

### 2.1 Create New Static Site

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Static Site"**
3. Connect your GitHub repository: `Sharan41/Medscribe-AI`
4. Select the repository

### 2.2 Configure Frontend Service

**Basic Settings:**
- **Name**: `medscribe-frontend` (or your preferred name)
- **Branch**: `main`
- **Root Directory**: `frontend`

**Build & Deploy:**
- **Build Command**: 
  ```bash
  npm install && npm run build
  ```
- **Publish Directory**: `dist`

**Advanced Settings:**
- **Auto-Deploy**: `Yes`
- **Pull Request Previews**: `Yes` (optional)

### 2.3 Environment Variables (Frontend)

Add these in the **Environment** section:

```env
# Backend API URL (use your backend Render URL)
VITE_API_URL=https://medscribe-backend.onrender.com

# Supabase (for direct client access if needed)
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Important:** 
- Frontend environment variables must be prefixed with `VITE_` to be accessible in the React app
- Update `VITE_API_URL` with your actual backend URL

### 2.4 Update Frontend API Configuration

Make sure your frontend `src/services/api.ts` uses the environment variable:

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### 2.5 Deploy Frontend

1. Click **"Create Static Site"**
2. Render will build and deploy
3. Wait for deployment (usually 3-5 minutes)
4. Note your frontend URL: `https://medscribe-frontend.onrender.com`

---

## ⚙️ Step 3: Configure Environment Variables

### 3.1 Update Backend CORS

After deploying frontend, update backend CORS:

1. Go to Backend Service → **Environment**
2. Update `CORS_ORIGINS`:
   ```env
   CORS_ORIGINS=https://medscribe-frontend.onrender.com,http://localhost:5173
   ```
3. **Save Changes** → Render will auto-redeploy

### 3.2 Update Frontend API URL

1. Go to Frontend Service → **Environment**
2. Ensure `VITE_API_URL` points to your backend:
   ```env
   VITE_API_URL=https://medscribe-backend.onrender.com
   ```
3. **Save Changes** → Render will auto-redeploy

---

## 🗄️ Step 4: Database Setup

### 4.1 Supabase Configuration

Your Supabase database is already configured. Ensure:

1. **Database Migrations**: Run all migrations in Supabase SQL Editor:
   - `backend/migrations/001_initial_schema.sql`
   - `backend/migrations/002_fix_rls_for_service_role.sql`
   - `backend/migrations/003_fix_storage_policies.sql`
   - `backend/migrations/004_disable_audit_logs_rls.sql`

2. **Storage Buckets**: Create storage buckets in Supabase:
   - `audio-files` (for audio uploads)
   - `pdf-files` (for generated PDFs)

3. **RLS Policies**: Verify Row Level Security policies are set correctly

### 4.2 Storage Configuration

In Supabase Dashboard → Storage:

1. Create bucket: `audio-files`
   - **Public**: `No` (private)
   - **File size limit**: 50MB
   - **Allowed MIME types**: `audio/*`

2. Create bucket: `pdf-files`
   - **Public**: `Yes` (for PDF downloads)
   - **File size limit**: 10MB
   - **Allowed MIME types**: `application/pdf`

---

## ✅ Step 5: Test Deployment

### 5.1 Test Backend

1. Visit backend docs: `https://medscribe-backend.onrender.com/docs`
2. Test health endpoint: `https://medscribe-backend.onrender.com/api/health`
3. Verify API is accessible

### 5.2 Test Frontend

1. Visit frontend: `https://medscribe-frontend.onrender.com`
2. Try registering a new user
3. Test creating a consultation
4. Verify PDF generation

### 5.3 Test End-to-End Flow

1. **Register/Login**: Create an account
2. **Upload Audio**: Upload a test audio file
3. **Generate SOAP**: Wait for SOAP note generation
4. **Download PDF**: Download the generated PDF

---

## 🔧 Troubleshooting

### Backend Issues

#### Build Fails: "Module not found"
- **Solution**: Ensure `requirements.txt` includes all dependencies
- Check `backend/requirements.txt` is complete

#### Runtime Error: "Port already in use"
- **Solution**: Use `$PORT` environment variable in start command:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

#### CORS Errors
- **Solution**: Update `CORS_ORIGINS` in backend environment variables
- Include both production and development URLs

#### Database Connection Errors
- **Solution**: Verify Supabase credentials in environment variables
- Check Supabase project is active and accessible

### Frontend Issues

#### Build Fails: "Cannot find module"
- **Solution**: Ensure `package.json` has all dependencies
- Run `npm install` locally to verify

#### API Calls Fail: "Network Error"
- **Solution**: Check `VITE_API_URL` is set correctly
- Verify backend CORS allows frontend origin
- Check backend is running and accessible

#### Environment Variables Not Working
- **Solution**: Ensure variables are prefixed with `VITE_`
- Rebuild frontend after adding environment variables

### Common Render Issues

#### Service Goes to Sleep (Free Plan)
- **Issue**: Free tier services sleep after 15 minutes of inactivity
- **Solution**: 
  - Upgrade to paid plan for always-on service
  - Or use a ping service to keep it awake (not recommended for production)

#### Slow Cold Starts
- **Issue**: First request after sleep takes 30-60 seconds
- **Solution**: Upgrade to paid plan for faster cold starts

#### Build Timeout
- **Issue**: Build takes longer than 20 minutes
- **Solution**: 
  - Optimize dependencies
  - Use `.dockerignore` to exclude unnecessary files
  - Consider using Docker for faster builds

---

## 📝 Additional Configuration Files

### Create `render.yaml` (Root Directory)

```yaml
services:
  - type: web
    name: medscribe-backend
    runtime: python
    plan: free
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: CORS_ORIGINS
        sync: false

  - type: web
    name: medscribe-frontend
    runtime: static
    rootDir: frontend
    buildCommand: npm install && npm run build
    staticPublishPath: dist
    envVars:
      - key: VITE_API_URL
        sync: false
      - key: VITE_SUPABASE_URL
        sync: false
      - key: VITE_SUPABASE_ANON_KEY
        sync: false
```

### Update `backend/app/main.py` for Render

Ensure your FastAPI app uses the PORT environment variable:

```python
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
```

---

## 🚀 Quick Deployment Checklist

- [ ] Create Render account
- [ ] Deploy backend service
- [ ] Configure backend environment variables
- [ ] Deploy frontend service
- [ ] Configure frontend environment variables
- [ ] Update backend CORS with frontend URL
- [ ] Run database migrations in Supabase
- [ ] Create storage buckets in Supabase
- [ ] Test backend API (`/docs` endpoint)
- [ ] Test frontend application
- [ ] Test end-to-end flow (register → upload → generate → download)

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)
- [Supabase Documentation](https://supabase.com/docs)

---

## 💡 Pro Tips

1. **Use Environment Groups**: Create environment groups in Render for shared variables
2. **Monitor Logs**: Check Render logs for debugging issues
3. **Set Up Alerts**: Configure email alerts for deployment failures
4. **Use Custom Domains**: Add custom domains for production
5. **Enable SSL**: Render provides free SSL certificates automatically
6. **Database Backups**: Set up regular Supabase backups
7. **Performance**: Consider upgrading to paid plan for production use

---

**Need Help?** Open an issue on [GitHub](https://github.com/Sharan41/Medscribe-AI/issues)

