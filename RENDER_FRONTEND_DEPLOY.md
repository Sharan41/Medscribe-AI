# 🎨 Deploy Frontend to Render (Manual)

Render Blueprints don't support static sites, so the frontend must be deployed separately.

## Quick Steps

### 1. Deploy Backend First (via Blueprint)

The `render.yaml` will deploy the backend automatically. Wait for it to complete.

### 2. Deploy Frontend Manually

1. **Go to Render Dashboard**
   - Visit [dashboard.render.com](https://dashboard.render.com)
   - Click **"New +"** → **"Static Site"**

2. **Connect Repository**
   - Select **"Connect GitHub"**
   - Choose repository: `Sharan41/Medscribe-AI`
   - Click **"Connect"**

3. **Configure Settings**
   - **Name**: `medscribe-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: 
     ```bash
     npm install && npm run build
     ```
   - **Publish Directory**: `dist`

4. **Add Environment Variables**
   Click **"Advanced"** → **"Add Environment Variable"**:
   
   ```
   VITE_API_URL=https://medscribe-backend.onrender.com
   ```
   
   **Important:** Replace `medscribe-backend.onrender.com` with your actual backend URL from step 1.

   Optional (if using Supabase directly in frontend):
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

5. **Deploy**
   - Click **"Create Static Site"**
   - Wait 3-5 minutes for build and deployment
   - Note your frontend URL: `https://medscribe-frontend.onrender.com`

### 3. Update Backend CORS

After frontend is deployed:

1. Go to **Backend Service** → **Environment**
2. Update `CORS_ORIGINS`:
   ```
   https://medscribe-frontend.onrender.com,http://localhost:5173
   ```
3. **Save** (auto-redeploys backend)

### 4. Test

1. Visit your frontend URL
2. Try registering/login
3. Test creating a consultation
4. Verify PDF generation

## Troubleshooting

### Build Fails

**Check logs:**
- Go to Frontend service → **Logs**
- Look for TypeScript or dependency errors

**Common fixes:**
- Ensure `package.json` has all dependencies
- Check for TypeScript errors locally first:
  ```bash
  cd frontend
  npm install
  npm run build
  ```

### Environment Variables Not Working

- Variables must start with `VITE_`
- Rebuild required after adding variables
- Check in browser console: `console.log(import.meta.env)`

### API Connection Fails

- Verify `VITE_API_URL` is correct
- Check backend is running: Visit `https://medscribe-backend.onrender.com/docs`
- Verify CORS is configured correctly

## Alternative: Deploy Both Manually

If Blueprint continues to cause issues:

1. **Delete the Blueprint**
2. **Deploy Backend Manually:**
   - New → Web Service
   - Configure as per `render.yaml` backend section
3. **Deploy Frontend Manually:**
   - Follow steps above

---

**Note:** Static sites on Render are free and don't sleep, making them perfect for frontend applications!

