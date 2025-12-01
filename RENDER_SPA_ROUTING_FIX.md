# 🔧 Fix: "Page Not Found" on Refresh (SPA Routing)

**Issue:** When refreshing pages on Render (e.g., `/dashboard`, `/consultations/123`), you get a "404 Not Found" error.

**Root Cause:** Single Page Applications (SPAs) need server-side configuration to redirect all routes to `index.html`. Render static sites need a `_redirects` file.

---

## ✅ Solution

### **Step 1: Verify `_redirects` File**

The file should be at: `frontend/public/_redirects`

**Content:**
```
/*    /index.html   200
```

**Format:** `[path] [destination] [status code]`
- `/*` = All paths
- `/index.html` = Redirect to index.html
- `200` = HTTP 200 status (not a redirect, but serves the file)

### **Step 2: Verify Build Output**

After running `npm run build`, check that `dist/_redirects` exists:

```bash
cd frontend
npm run build
ls -la dist/_redirects
```

If the file exists in `dist/`, Vite is copying it correctly.

### **Step 3: Configure Render Static Site**

1. **Go to Render Dashboard**
   - Navigate to your Frontend Static Site service
   - Click on **"Settings"**

2. **Check Build Configuration**
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`

3. **Verify `_redirects` File is Deployed**
   - After deployment, check the deployed files
   - The `_redirects` file should be in the root of the deployed site
   - You can verify by visiting: `https://your-frontend.onrender.com/_redirects`
   - It should show: `/*    /index.html   200`

### **Step 4: Manual Redeploy (If Needed)**

If the `_redirects` file isn't working:

1. **Trigger Manual Deploy**
   - Go to your Frontend service in Render
   - Click **"Manual Deploy"** → **"Deploy latest commit"**
   - Wait for deployment to complete

2. **Clear Browser Cache**
   - Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
   - Or clear browser cache completely

---

## 🔍 Troubleshooting

### **Issue: Still Getting 404 on Refresh**

**Possible Causes:**

1. **`_redirects` file not in build output**
   - Check: `frontend/dist/_redirects` exists after build
   - Fix: Ensure file is in `frontend/public/_redirects`

2. Render not recognizing `_redirects`**
   - Some Render configurations need explicit redirect rules
   - Alternative: Use `render.yaml` with redirect configuration

**3. Browser Cache**
   - Clear browser cache
   - Try incognito/private window

**4. Wrong Publish Directory**
   - Verify: **Publish Directory** = `dist` (not `frontend/dist`)

### **Alternative: Use `render.yaml`**

If `_redirects` doesn't work, configure redirects in `render.yaml`:

```yaml
services:
  - type: static
    name: medscribe-frontend
    rootDir: frontend
    buildCommand: npm install && npm run build
    staticPublishPath: dist
    headers:
      - path: /*
        name: X-Robots-Tag
        value: noindex
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

---

## ✅ Verification

After deployment, test these URLs:

1. **Root:** `https://your-frontend.onrender.com/` ✅ Should work
2. **Login:** `https://your-frontend.onrender.com/login` ✅ Should work (even on refresh)
3. **Dashboard:** `https://your-frontend.onrender.com/dashboard` ✅ Should work (even on refresh)
4. **Consultation:** `https://your-frontend.onrender.com/consultations/[id]` ✅ Should work (even on refresh)

**Test Method:**
- Navigate to `/dashboard`
- Refresh the page (F5 or Cmd+R)
- Should NOT show 404 error

---

## 📝 Notes

- **When does this happen?**
  - Only when refreshing pages (not when navigating via links)
  - Happens because the browser requests `/dashboard` from the server
  - Server doesn't have a `/dashboard` file, only `index.html`
  - `_redirects` tells Render to serve `index.html` for all routes

- **Does this happen on every deployment?**
  - No, once configured correctly, it persists
  - Only happens if `_redirects` file is missing or misconfigured
  - If you see 404 after a new deployment, check that `_redirects` is still in `dist/`

---

## 🎯 Quick Fix Checklist

- [ ] `frontend/public/_redirects` exists with content: `/*    /index.html   200`
- [ ] `frontend/dist/_redirects` exists after `npm run build`
- [ ] Render **Publish Directory** is set to `dist`
- [ ] Manual redeploy triggered after adding `_redirects`
- [ ] Browser cache cleared
- [ ] Tested refresh on `/dashboard` and `/login` pages

