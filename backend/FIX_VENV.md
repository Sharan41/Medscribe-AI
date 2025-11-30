# Fix: ModuleNotFoundError - Virtual Environment Issue

## Problem
You're running uvicorn with system Python 3.13 instead of the virtual environment (Python 3.11) where dependencies are installed.

## Solution

### Option 1: Use the Start Script (Easiest)
```bash
cd backend
./START_SERVER.sh
```

### Option 2: Manual Activation
```bash
cd backend
source venv/bin/activate  # IMPORTANT: Activate venv first!
uvicorn app.main:app --reload
```

### Option 3: Check Virtual Environment
```bash
cd backend
source venv/bin/activate
which python  # Should show: .../backend/venv/bin/python
python --version  # Should show: Python 3.11.x
```

## Verify It's Working

After activating venv, check:
```bash
python -c "import supabase; print('✅ Supabase found')"
python -c "import fastapi; print('✅ FastAPI found')"
```

If you see errors, the venv isn't activated!

## Quick Fix Command

```bash
cd "/Users/saisharan.v/Desktop/new project/backend"
source venv/bin/activate
uvicorn app.main:app --reload
```

---

**Remember:** Always activate the virtual environment before running the server!

