# 🚀 How to Run the Server Correctly

## ❌ **What Was Wrong**

You were running commands from the **root directory** (`/Users/saisharan.v/Desktop/new project/`), but:
- The `venv` is in `backend/venv/`
- The `app` module is in `backend/app/`
- Uvicorn needs to run from `backend/` directory

## ✅ **Correct Way to Run**

### **Option 1: Use the Start Script (Easiest)**

```bash
cd "/Users/saisharan.v/Desktop/new project/backend"
bash START_SERVER_FIXED.sh
```

### **Option 2: Manual Commands**

```bash
# Step 1: Change to backend directory
cd "/Users/saisharan.v/Desktop/new project/backend"

# Step 2: Activate virtual environment
source venv/bin/activate

# Step 3: Run uvicorn (from backend directory)
uvicorn app.main:app --port 8000
```

### **Option 3: One-Liner**

```bash
cd "/Users/saisharan.v/Desktop/new project/backend" && source venv/bin/activate && uvicorn app.main:app --port 8000
```

## 🔍 **Why It Failed**

1. **`source venv/bin/activate`** failed because you were in root, but venv is in `backend/venv/`
2. **`ModuleNotFoundError: No module named 'app'`** happened because:
   - You need to be in `backend/` directory where `app/` folder exists
   - Python looks for modules relative to current directory

## ⚠️ **If You Get "ModuleNotFoundError: No module named 'fastapi'"**

This means dependencies aren't installed in the virtual environment. Install them:

```bash
cd "/Users/saisharan.v/Desktop/new project/backend"
source venv/bin/activate
pip install -r requirements.txt
```

## ✅ **Quick Test**

Run this to verify you're in the right place:

```bash
cd "/Users/saisharan.v/Desktop/new project/backend"
ls -la app/main.py  # Should show the file
source venv/bin/activate
python -c "import fastapi; import app.main; print('✅ All modules found!')"
```

## 📝 **Summary**

**Always run uvicorn from the `backend/` directory, not the root!**

