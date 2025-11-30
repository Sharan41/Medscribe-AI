# 🔧 WeasyPrint Dependencies Fix

**Issue:** Server won't start because WeasyPrint requires system libraries.

**Error:** `OSError: cannot load library 'libgobject-2.0-0'`

---

## ✅ Quick Fix Applied

**Made PDF generation lazy-loaded:**
- ✅ PDF service no longer imported at startup
- ✅ Server can start without WeasyPrint dependencies
- ✅ PDF endpoint will show error if dependencies missing
- ✅ Other endpoints work fine

---

## 🔧 To Enable PDF Generation (Optional)

**Install WeasyPrint dependencies:**

**macOS:**
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Then restart server:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## ✅ Current Status

- ✅ **Server starts** without PDF dependencies
- ✅ **All other features work** (upload, transcription, SOAP)
- ⏳ **PDF generation** requires additional dependencies

---

**Server should start now!** 🚀

