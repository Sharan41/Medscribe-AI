# Quick Start Guide - Backend

## ✅ Setup Complete!

**Status:** All dependencies installed ✅  
**Location:** `/Users/saisharan.v/Desktop/new project/backend`

---

## 📍 Important Files

### `.env` File Location
```
backend/.env
```

**Contains:**
- Supabase credentials
- Groq API key
- Reverie API keys
- All configuration

---

## 🚀 Start Backend Server

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Server will start at:** http://localhost:8000

**API Documentation:** http://localhost:8000/docs

---

## ✅ Test Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. API Docs
Open in browser: http://localhost:8000/docs

### 3. Register User
- Go to `/docs`
- Try POST `/auth/register`
- Body:
  ```json
  {
    "email": "test@example.com",
    "password": "Test123!",
    "name": "Dr. Test",
    "clinic_name": "Test Clinic"
  }
  ```

---

## 📋 Next Steps

1. **Run Database Migration:**
   - Go to Supabase Dashboard
   - SQL Editor → Run `backend/migrations/001_initial_schema.sql`

2. **Create Storage Buckets:**
   - Storage → Create `audio-files` and `notes` buckets

3. **Test Backend:**
   - Start server
   - Test registration/login

---

**Ready to go!** 🎉

