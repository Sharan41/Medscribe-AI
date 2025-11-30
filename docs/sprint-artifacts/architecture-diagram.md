# System Architecture: MedScribe AI

**Document Type:** System Architecture Design  
**Project:** MedScribe AI - Indian Medical Transcription Assistant  
**Version:** 1.0  
**Date:** November 29, 2024  
**Architect:** Architect Agent 🏛️

---

## 🏗️ High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │  Web Browser │         │  Mobile Web  │                     │
│  │   (React)    │         │   (React)    │                     │
│  └──────┬───────┘         └──────┬───────┘                     │
│         │                        │                              │
│         └────────────┬───────────┘                              │
│                      │                                          │
│                      │ HTTPS/TLS 1.3                            │
└──────────────────────┼──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (Python 3.11)               │  │
│  │  - Authentication & Authorization                        │  │
│  │  - Request Routing                                       │  │
│  │  - Rate Limiting                                         │  │
│  │  - Request Validation                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION SERVICES LAYER                    │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Audio      │  │ Transcription│  │   SOAP      │          │
│  │  Recording   │  │   Service    │  │ Generation  │          │
│  │   Service    │  │              │  │   Service   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                   │
│         │                 │                  │                   │
└─────────┼─────────────────┼──────────────────┼──────────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES LAYER                      │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Reverie    │  │    Groq      │  │   Hugging    │          │
│  │  API (STT)   │  │   LLM API    │  │    Face      │          │
│  │              │  │              │  │   (NER)      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐                                              │
│  │   Whisper    │  (Fallback for STT)                          │
│  │   (Local)    │                                              │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Supabase (PostgreSQL + RLS)                  │  │
│  │                                                            │  │
│  │  - Users (with RLS)                                       │  │
│  │  - Consultations (with RLS)                               │  │
│  │  - Notes (JSONB for flexible SOAP)                        │  │
│  │  - Transcripts (JSONB)                                    │  │
│  │  - Audit Logs (with RLS)                                  │  │
│  │  - Clinic Profiles                                         │  │
│  │                                                            │  │
│  │  Row Level Security: Auto-enforces DPDP per-doctor        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────┐                                              │
│  │ File Storage │  Supabase Storage (or S3)                    │
│  │              │  - Audio files                                │
│  │              │  - Exported PDFs                              │
│  └──────────────┘                                              │
│                                                                  │
│  ┌──────────────┐                                              │
│  │ Redis Queue  │  Celery (Async Processing)                  │
│  │              │  - Transcription jobs                         │
│  │              │  - SOAP generation jobs                       │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Architecture

### Flow 1: Unified Consultation Processing (Optimized)

```
User (Doctor)
    │
    ├─> POST /consultations
    │   ├─> Uploads Audio File
    │   ├─> Language: "ta" | "te"
    │   └─> Patient Name (optional)
    │
    ▼
FastAPI Backend
    │
    ├─> Validates File (size, format)
    │
    ├─> Stores Audio (Supabase Storage)
    │
    ├─> Creates Consultation Record (Supabase)
    │   └─> Status: "processing"
    │
    ├─> Returns Consultation ID + WebSocket URL
    │
    ▼
Celery Background Queue
    │
    ├─> Task 1: Transcription (Reverie API)
    │   ├─> Calls Reverie API
    │   ├─> Updates: transcript + confidence
    │   └─> Status: "transcribed"
    │
    ├─> Task 2: Entity Extraction (Hugging Face)
    │   ├─> Extracts entities
    │   └─> Updates: entities
    │
    ├─> Task 3: SOAP Generation (Groq LLM)
    │   ├─> Generates SOAP note
    │   ├─> Updates: soap_note
    │   └─> Status: "completed"
    │
    ├─> WebSocket Notification
    │   └─> Real-time update to frontend
    │
    ▼
Frontend (Polling or WebSocket)
    │
    ├─> GET /consultations/{id}
    │   └─> Returns complete consultation data
    │
    └─> GET /notes/{id}/pdf
        └─> Downloads professional PDF
```

### Flow 2: Unified Consultation Flow (Optimized)

```
POST /consultations
    │
    ├─> Audio Upload
    ├─> Create Consultation Record
    ├─> Queue Background Jobs
    │
    └─> Return: {consultation_id, status: "processing", websocket_url}

Background Processing (Celery):
    │
    ├─> Transcription (Reverie)
    ├─> Entity Extraction (Hugging Face)
    ├─> SOAP Generation (Groq)
    ├─> PDF Generation (WeasyPrint)
    ├─> ICD Code Extraction (optional)
    │
    └─> Update Status: "completed"

Frontend Options:
    │
    ├─> Option 1: WebSocket (Real-time)
    │   └─> wss://api.medscribe.ai/ws/{consultation_id}
    │
    └─> Option 2: Polling (Standard)
        └─> GET /consultations/{id} (every 2 seconds)

When Complete:
    │
    ├─> GET /consultations/{id}
    │   └─> Returns: {transcript, soap_note, pdf_url, fhir_bundle}
    │
    └─> GET /notes/{id}/pdf
        └─> Downloads professional PDF
```

---

## 🧩 Component Architecture

### Frontend Components (React)

```
MedScribe App
├── Authentication
│   ├── Login Component
│   ├── Register Component
│   └── Auth Context
│
├── Dashboard
│   ├── Recent Notes List
│   ├── Quick Record Button
│   └── Search Component
│
├── Recording
│   ├── Audio Recorder Component
│   ├── File Upload Component
│   └── Recording Status
│
├── Transcription
│   ├── Transcript Display
│   ├── Transcript Editor
│   └── Language Selector
│
├── Notes
│   ├── SOAP Note Viewer
│   ├── SOAP Note Editor
│   ├── Note List Component
│   └── Note Detail Component
│
└── Settings
    ├── Profile Settings
    └── Language Preferences
```

### Backend Services (FastAPI)

```
FastAPI Application
├── API Routes
│   ├── /auth/* (Authentication)
│   ├── /audio/* (Audio Management)
│   ├── /transcription/* (Transcription)
│   ├── /notes/* (SOAP Notes)
│   └── /users/* (User Management)
│
├── Services
│   ├── AuthService (JWT, Password Hashing)
│   ├── AudioService (File Handling)
│   ├── TranscriptionService (Reverie Integration)
│   ├── SOAPGenerationService (LLM + NER)
│   └── NoteService (CRUD Operations)
│
├── Models
│   ├── User Models (Pydantic)
│   ├── Note Models (Pydantic)
│   └── Request/Response Models
│
└── Middleware
    ├── Authentication Middleware
    ├── Error Handling Middleware
    └── Logging Middleware
```

---

## 🔌 Integration Architecture

### Reverie API Integration

```
Transcription Service
    │
    ├─> Initialize Reverie Client
    │   └─> API Key: Environment Variable
    │   └─> App ID: Environment Variable
    │
    ├─> Prepare Audio
    │   ├─> Read Audio File
    │   ├─> Validate Format (MP3/WAV)
    │   └─> Check Size (<50MB)
    │
    ├─> Call Reverie API
    │   ├─> POST /asr/stt_file
    │   ├─> Parameters:
    │   │   ├─> src_lang: "ta" | "te"
    │   │   ├─> data: audio_bytes
    │   │   ├─> format: "mp3" | "wav"
    │   │   └─> punctuate: "true"
    │   │
    │   └─> Response:
    │       ├─> text: transcript
    │       ├─> confidence: float
    │       └─> success: bool
    │
    ├─> Error Handling
    │   ├─> Retry Logic (3 attempts)
    │   ├─> Fallback to Whisper (if fails)
    │   └─> Log Errors
    │
    └─> Cost Monitoring
        ├─> Track API Calls
        ├─> Calculate Cost (₹0.50/min)
        └─> Alert at 80% budget (₹4K)
```

### Groq LLM Integration

```
SOAP Generation Service
    │
    ├─> Initialize Groq Client
    │   └─> API Key: Environment Variable
    │
    ├─> Create Prompt
    │   ├─> System Message (Medical Assistant)
    │   ├─> Few-shot Examples
    │   ├─> Transcript Input
    │   └─> Language Context
    │
    ├─> Call Groq API
    │   ├─> POST /chat/completions
    │   ├─> Model: "llama-3.1-70b-versatile"
    │   ├─> Parameters:
    │   │   ├─> max_tokens: 1000
    │   │   ├─> temperature: 0.3
    │   │   └─> messages: [system, user]
    │   │
    │   └─> Response:
    │       ├─> content: SOAP note
    │       └─> usage: tokens
    │
    ├─> Validate Output
    │   ├─> Check SOAP sections present
    │   ├─> Validate medical accuracy
    │   └─> Flag low-confidence sections
    │
    └─> Fallback Strategy
        └─> Use rule-based if LLM fails
```

### Hugging Face NER Integration

```
Entity Extraction Service
    │
    ├─> Load Models
    │   ├─> Medical NER: "AventIQ-AI/bert-medical-entity-extraction"
    │   └─> Indic-BERT: "ai4bharat/indic-bert" (Tamil/Telugu)
    │
    ├─> Extract Entities
    │   ├─> Method 1: Indic-BERT (for Tamil/Telugu)
    │   ├─> Method 2: Medical NER (for English/translated)
    │   └─> Method 3: Rule-based (common terms)
    │
    ├─> Merge Results
    │   ├─> Deduplicate entities
    │   ├─> Combine confidence scores
    │   └─> Categorize by type
    │
    └─> Return Entities
        └─> List of {word, type, confidence}
```

---

## 🗄️ Database Architecture

### PostgreSQL Schema (Structured Data)

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    clinic_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Consultations Table
CREATE TABLE consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    patient_name VARCHAR(255),
    language VARCHAR(10) NOT NULL, -- 'ta', 'te'
    audio_file_path VARCHAR(500),
    audio_duration INTEGER, -- seconds
    status VARCHAR(50) DEFAULT 'pending', -- pending, transcribing, completed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Notes Metadata Table
CREATE TABLE notes_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_id UUID REFERENCES consultations(id),
    user_id UUID REFERENCES users(id),
    note_mongodb_id VARCHAR(255) NOT NULL, -- Reference to MongoDB
    title VARCHAR(255),
    language VARCHAR(10),
    confidence_score FLOAT,
    edit_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Audit Logs Table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL, -- 'create', 'read', 'update', 'delete'
    resource_type VARCHAR(50), -- 'note', 'consultation'
    resource_id UUID,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_consultations_user_id ON consultations(user_id);
CREATE INDEX idx_consultations_status ON consultations(status);
CREATE INDEX idx_notes_user_id ON notes_metadata(user_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

### MongoDB Schema (Flexible Notes)

```javascript
// Notes Collection
{
  "_id": ObjectId,
  "consultation_id": "uuid",
  "user_id": "uuid",
  "patient_name": "string",
  "language": "ta" | "te",
  
  // Transcript
  "transcript": {
    "text": "string",
    "confidence": 0.65,
    "entities": [
      {
        "word": "காய்ச்சல்",
        "type": "SYMPTOM",
        "confidence": 0.95
      }
    ]
  },
  
  // SOAP Note
  "soap_note": {
    "subjective": ["symptom1", "symptom2"],
    "objective": ["finding1", "finding2"],
    "assessment": ["diagnosis1"],
    "plan": [
      {
        "medication": "பாராசிட்டமால்",
        "dosage": "500mg",
        "frequency": "3 times daily"
      }
    ],
    "formatted": "markdown string",
    "generation_method": "hybrid" | "llm_only" | "rule_based"
  },
  
  // Metadata
  "created_at": ISODate,
  "updated_at": ISODate,
  "version": 1
}

// Transcripts Collection (for history)
{
  "_id": ObjectId,
  "consultation_id": "uuid",
  "transcript": "string",
  "language": "ta" | "te",
  "confidence": 0.65,
  "created_at": ISODate
}
```

---

## 🔒 Security Architecture

### Authentication Flow

```
User Login
    │
    ├─> POST /auth/login
    │   ├─> Email + Password
    │   │
    │   ├─> Validate Credentials
    │   │   ├─> Check Email in DB
    │   │   ├─> Verify Password (bcrypt)
    │   │   └─> Check Active Status
    │   │
    │   ├─> Generate JWT Token
    │   │   ├─> Payload: {user_id, email, exp}
    │   │   ├─> Secret: Environment Variable
    │   │   └─> Expiry: 24 hours
    │   │
    │   └─> Return Token + Refresh Token
    │
    └─> Store Token (Frontend)
        └─> Include in Subsequent Requests
```

### Authorization Flow

```
API Request
    │
    ├─> Extract JWT Token (Header)
    │
    ├─> Verify Token
    │   ├─> Check Signature
    │   ├─> Check Expiry
    │   └─> Extract User ID
    │
    ├─> Check Resource Access
    │   ├─> User can only access own notes
    │   └─> Role-based checks (if needed)
    │
    └─> Allow/Deny Request
```

### Data Encryption

```
Data at Rest:
    │
    ├─> Database Fields
    │   ├─> Sensitive fields: AES-256 encryption
    │   ├─> Patient names: Encrypted
    │   └─> Notes: Encrypted in MongoDB
    │
    └─> File Storage
        └─> Audio files: Encrypted (S3 encryption)

Data in Transit:
    │
    └─> TLS 1.3
        ├─> All API calls: HTTPS
        ├─> Database connections: SSL
        └─> External API calls: HTTPS
```

---

## 🚀 Deployment Architecture

### Production Deployment

```
┌─────────────────────────────────────────┐
│         Load Balancer (Nginx)           │
│         - SSL Termination                │
│         - Rate Limiting                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      FastAPI Backend (Docker)           │
│      - Multiple Instances (2-3)         │
│      - Auto-scaling                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Database Layer                     │
│      - PostgreSQL (Managed)            │
│      - MongoDB (Managed)                │
│      - File Storage (S3)                │
└─────────────────────────────────────────┘
```

### Environment Configuration

```
Production:
- API_URL: https://api.medscribe.ai
- Database: Managed PostgreSQL + MongoDB
- File Storage: AWS S3
- Monitoring: Sentry, CloudWatch

Development:
- API_URL: http://localhost:8000
- Database: Local PostgreSQL + MongoDB
- File Storage: Local filesystem
- Monitoring: Local logs
```

---

## 📊 Performance Architecture

### Caching Strategy

```
┌─────────────────────────────────────────┐
│         Redis Cache Layer                │
│                                          │
│  - User Sessions                        │
│  - Frequently accessed notes            │
│  - NER Model Results (5 min TTL)        │
│  - API Rate Limits                      │
└─────────────────────────────────────────┘
```

### Async Processing

```
Long-Running Tasks:
    │
    ├─> Transcription (can take 5-10 seconds)
    │   └─> Use Celery + Redis
    │   └─> Background job queue
    │
    └─> SOAP Generation (can take 2-3 seconds)
        └─> Use FastAPI BackgroundTasks
        └─> Return job ID, poll for status
```

---

## 🔄 Error Handling & Resilience

### Retry Strategy

```
API Calls:
    │
    ├─> Reverie API
    │   ├─> Retry: 3 attempts
    │   ├─> Exponential backoff
    │   └─> Fallback: Whisper
    │
    ├─> Groq LLM
    │   ├─> Retry: 2 attempts
    │   └─> Fallback: Rule-based
    │
    └─> Hugging Face
        └─> Retry: 2 attempts
```

### Circuit Breaker Pattern

```
External API Calls:
    │
    ├─> Monitor Failure Rate
    │   ├─> If >50% failures: Open circuit
    │   └─> Use fallback immediately
    │
    └─> After 60 seconds: Try again
```

---

## 📈 Monitoring & Observability

### Metrics to Track

```
Application Metrics:
- API Response Times (p50, p95, p99)
- Error Rates (4xx, 5xx)
- Transcription Success Rate
- SOAP Generation Success Rate
- Cost per Note (Reverie + Groq)

Business Metrics:
- Notes Created per Day
- Average Edit Time
- User Satisfaction Score
- Daily Active Users
```

### Logging Strategy

```
Log Levels:
- ERROR: API failures, exceptions
- WARN: Retries, fallbacks
- INFO: User actions, API calls
- DEBUG: Detailed request/response

Log Aggregation:
- Centralized logging (ELK/CloudWatch)
- Structured logs (JSON)
- Correlation IDs for tracing
```

---

## ✅ Architecture Decisions

### Key Decisions Made

1. **Microservices vs Monolith**
   - **Decision:** Monolithic FastAPI app (simpler for MVP)
   - **Reason:** Faster development, easier deployment

2. **Database Choice**
   - **Decision:** PostgreSQL + MongoDB
   - **Reason:** Structured data (users) + Flexible notes

3. **Authentication**
   - **Decision:** JWT tokens
   - **Reason:** Stateless, scalable, simple

4. **File Storage**
   - **Decision:** S3 (production) / Local (dev)
   - **Reason:** Scalable, reliable

5. **Caching**
   - **Decision:** Redis (optional for MVP)
   - **Reason:** Performance optimization

---

## 🎯 Next Steps

1. **API Specification** - Detailed endpoint design
2. **Database Schema** - Complete schema with migrations
3. **Security Architecture** - Detailed security plan
4. **Integration Design** - Detailed integration specs
5. **Implementation Readiness** - Pre-coding checklist

---

**Document Status:** ✅ Complete  
**Ready for:** API Design & Database Schema  
**Next Document:** `api-specification.md`

---

**Last Updated:** November 29, 2024  
**Version:** 1.0

