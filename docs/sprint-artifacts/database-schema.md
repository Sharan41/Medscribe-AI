# Database Schema: MedScribe AI

**Document Type:** Database Design Specification  
**Project:** MedScribe AI  
**Version:** 1.0  
**Date:** November 29, 2024

---

## 🗄️ Database Architecture Overview (Optimized)

**Single-Database Approach: Supabase (PostgreSQL + RLS)**
- **Supabase:** PostgreSQL database with Row Level Security
- **JSONB:** Flexible document storage (notes, transcripts) in PostgreSQL
- **Storage:** Built-in file storage (audio files, PDFs)

**Why Supabase?**
- ✅ Single service (simpler than two databases)
- ✅ Row Level Security (auto-enforces DPDP per-doctor isolation)
- ✅ Built-in authentication
- ✅ Real-time subscriptions (WebSocket support)
- ✅ File storage included
- ✅ Free tier: 500MB DB, 1GB storage (scales to 50 doctors)
- ✅ JSONB for flexible notes (like MongoDB but in PostgreSQL)

**Migration from MongoDB:**
- Notes stored as JSONB in PostgreSQL
- Same flexibility, better performance
- Automatic RLS for security

---

## 📊 Supabase Schema (PostgreSQL + RLS)

### Users Table (Supabase Auth Integration)

**Note:** Uses Supabase Auth for authentication. Custom table for profile data.

```sql
-- Extend Supabase auth.users with profile
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    backup_codes TEXT[], -- Array of backup codes
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security Policy
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE INDEX idx_user_profiles_email ON user_profiles(email);
CREATE INDEX idx_user_profiles_active ON user_profiles(is_active);
```

---

### Clinic Profiles Table

```sql
CREATE TABLE clinic_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    clinic_name VARCHAR(255) NOT NULL,
    address TEXT,
    license_no VARCHAR(100),
    doctor_reg VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE clinic_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own clinic"
    ON clinic_profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own clinic"
    ON clinic_profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE INDEX idx_clinic_profiles_user_id ON clinic_profiles(user_id);
```

**Fields:**
- `id`: Unique user identifier
- `email`: Login email (unique, validated)
- `password_hash`: Bcrypt hashed password
- `name`: Doctor's name
- `clinic_name`: Clinic name
- `is_active`: Account status
- `is_verified`: Email verification status

---

### Consultations Table (Unified)

```sql
CREATE TABLE consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    patient_name VARCHAR(255),
    language VARCHAR(10) NOT NULL CHECK (language IN ('ta', 'te', 'hi')),
    
    -- Audio File
    audio_file_path VARCHAR(500), -- Supabase Storage path
    audio_file_size BIGINT, -- bytes
    audio_duration INTEGER, -- seconds
    audio_format VARCHAR(10), -- 'mp3', 'wav'
    
    -- Processing Status
    status VARCHAR(50) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed')),
    progress JSONB DEFAULT '{}', -- {transcription: "completed", soap_generation: "processing"}
    
    -- Transcript (JSONB - flexible)
    transcript JSONB, -- {text: "...", confidence: 0.65, method: "reverie"}
    
    -- Entities (JSONB array)
    entities JSONB DEFAULT '[]', -- [{word: "...", type: "SYMPTOM", ...}]
    
    -- SOAP Note (JSONB - flexible structure)
    soap_note JSONB, -- {subjective: [...], objective: [...], assessment: [...], plan: [...], formatted: "..."}
    
    -- Additional Data
    icd_codes TEXT[], -- ["R50.9", "G44.1"]
    pdf_url VARCHAR(500), -- Supabase Storage URL
    fhir_bundle JSONB, -- FHIR Bundle for ABDM
    
    -- Metadata
    generation_method VARCHAR(50), -- "hybrid" | "llm_only" | "rule_based"
    generation_time FLOAT, -- seconds
    cost DECIMAL(10, 4), -- Total cost (Reverie + Groq)
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    CONSTRAINT valid_duration CHECK (audio_duration > 0 AND audio_duration <= 1800) -- Max 30 min
);

-- Row Level Security
ALTER TABLE consultations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own consultations"
    ON consultations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own consultations"
    ON consultations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own consultations"
    ON consultations FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own consultations"
    ON consultations FOR DELETE
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_consultations_user_id ON consultations(user_id);
CREATE INDEX idx_consultations_status ON consultations(status);
CREATE INDEX idx_consultations_created_at ON consultations(created_at DESC);
CREATE INDEX idx_consultations_language ON consultations(language);

-- JSONB Indexes for efficient querying
CREATE INDEX idx_consultations_transcript ON consultations USING GIN (transcript);
CREATE INDEX idx_consultations_soap_note ON consultations USING GIN (soap_note);
CREATE INDEX idx_consultations_entities ON consultations USING GIN (entities);
```

**Fields:**
- `id`: Unique consultation identifier
- `user_id`: Foreign key to users
- `patient_name`: Patient name (optional)
- `language`: Transcription language ('ta', 'te', 'hi')
- `audio_file_path`: Path to audio file (S3 or local)
- `status`: Current processing status
- `transcription_id`: Reference to transcription result
- `note_id`: Reference to MongoDB note document

---

### Notes Table (Unified with Consultations)

**Note:** Notes are now part of consultations table (JSONB). Separate table only for search/indexing.

```sql
-- Notes view/index table for search (optional optimization)
CREATE TABLE notes_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_id UUID NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    patient_name VARCHAR(255),
    title VARCHAR(255),
    language VARCHAR(10) NOT NULL CHECK (language IN ('ta', 'te', 'hi')),
    search_text TSVECTOR, -- Full-text search
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE notes_index ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own notes"
    ON notes_index FOR SELECT
    USING (auth.uid() = user_id);

-- Full-text search index
CREATE INDEX idx_notes_search_text ON notes_index USING GIN (search_text);
CREATE INDEX idx_notes_user_id ON notes_index(user_id);
CREATE INDEX idx_notes_created_at ON notes_index(created_at DESC);
CREATE INDEX idx_notes_language ON notes_index(language);

-- Trigger to update search_text
CREATE OR REPLACE FUNCTION update_notes_search_text()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_text := 
        setweight(to_tsvector('english', COALESCE(NEW.patient_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER notes_search_text_update
    BEFORE INSERT OR UPDATE ON notes_index
    FOR EACH ROW EXECUTE FUNCTION update_notes_search_text();
```

**Fields:**
- `id`: Unique metadata identifier
- `consultation_id`: Foreign key to consultations
- `note_mongodb_id`: Reference to MongoDB document
- `confidence_score`: Transcription confidence (0-1)
- `generation_method`: How SOAP was generated
- `edit_count`: Number of times edited
- `is_deleted`: Soft delete flag

---

### Audit Logs Table (DPDP Compliance)

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    action VARCHAR(100) NOT NULL CHECK (action IN ('create', 'read', 'update', 'delete', 'login', 'logout', 'export', 'download')),
    resource_type VARCHAR(50) CHECK (resource_type IN ('note', 'consultation', 'user', 'audio', 'pdf', 'fhir')),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    request_id UUID, -- X-Request-ID header
    clinic_id UUID, -- X-Clinic-ID header
    details JSONB, -- Additional details
    created_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security (Users can only see own logs)
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own audit logs"
    ON audit_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_request_id ON audit_logs(request_id);

-- Partition by month for performance (for large scale)
-- CREATE TABLE audit_logs_2024_11 PARTITION OF audit_logs
--     FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
```

**Fields:**
- `id`: Unique log entry identifier
- `user_id`: User who performed action
- `action`: Action type
- `resource_type`: Type of resource accessed
- `resource_id`: ID of resource
- `ip_address`: Client IP address
- `details`: Additional JSON details

**Retention:** 7 years (medical records requirement)

---

### API Usage Tracking Table

```sql
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    service VARCHAR(50) NOT NULL CHECK (service IN ('reverie', 'groq', 'huggingface')),
    endpoint VARCHAR(255),
    request_size BIGINT, -- bytes
    response_size BIGINT, -- bytes
    duration_ms INTEGER, -- milliseconds
    cost DECIMAL(10, 4), -- Cost in INR
    status_code INTEGER,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_service ON api_usage(service);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at DESC);

-- For cost monitoring
CREATE INDEX idx_api_usage_cost ON api_usage(service, created_at DESC);
```

**Purpose:** Track API usage for cost monitoring and rate limiting

---

## 📄 JSONB Schema (Supabase PostgreSQL)

### Consultations Table JSONB Structure

**Note:** All flexible data stored as JSONB in `consultations` table (replaces MongoDB)

```sql
-- Example JSONB structure in consultations table

-- transcript JSONB column:
{
  "text": "நோயாளிக்கு காய்ச்சல் மற்றும் தலைவலி உள்ளது...",
  "confidence": 0.65,
  "language": "ta",
  "transcription_method": "reverie",
  "word_count": 25,
  "created_at": "2024-11-29T10:00:00Z"
}

-- entities JSONB column:
[
  {
    "word": "காய்ச்சல்",
    "type": "SYMPTOM",
    "confidence": 0.95,
    "source": "indic_bert",
    "english": "fever"
  },
  {
    "word": "பாராசிட்டமால்",
    "type": "MEDICATION",
    "confidence": 0.98,
    "source": "rule_based",
    "dosage": "500mg",
    "frequency": "3 times daily"
  }
]

-- soap_note JSONB column:
{
  "subjective": [
    "Fever [காய்ச்சல்]",
    "Headache [தலைவலி]"
  ],
  "objective": [
    "Blood Pressure: 120/80 mmHg",
    "Temperature: 101°F",
    "General appearance: Appears unwell"
  ],
  "assessment": [
    "Viral fever",
    "Rule out other causes if symptoms persist"
  ],
  "plan": [
    {
      "medication": "Paracetamol",
      "tamil_term": "பாராசிட்டமால்",
      "dosage": "500mg",
      "frequency": "3 times daily",
      "duration": "3 days"
    },
    {
      "instruction": "Rest and adequate hydration"
    },
    {
      "followup": "Return in 3 days if symptoms persist"
    }
  ],
  "formatted": "# Medical Consultation Note\n\n## Subjective\n...",
  "generation_method": "hybrid",
  "generation_time": 2.5,
  "llm_model": "llama-3.1-70b-versatile",
  "ner_models": ["indic_bert", "medical_ner"],
  "version": 1,
  "edit_history": [
    {
      "version": 1,
      "edited_at": "2024-11-29T10:15:00Z",
      "edited_by": "uuid",
      "changes": "Updated assessment section"
    }
  ]
}

-- fhir_bundle JSONB column (ABDM Phase 2):
{
  "resourceType": "Bundle",
  "type": "document",
  "entry": [
    {
      "resource": {
        "resourceType": "Observation",
        "code": {
          "coding": [{
            "system": "http://loinc.org",
            "code": "8480-6",
            "display": "Systolic blood pressure"
          }]
        }
      }
    },
    {
      "resource": {
        "resourceType": "Condition",
        "code": {
          "coding": [{
            "system": "http://hl7.org/fhir/sid/icd-10",
            "code": "R50.9",
            "display": "Fever, unspecified"
          }]
        }
      }
    }
  ]
}

-- Querying JSONB:
SELECT 
  id,
  patient_name,
  transcript->>'text' as transcript_text,
  transcript->>'confidence' as confidence,
  jsonb_array_length(entities) as entity_count,
  soap_note->'subjective' as subjective_section,
  icd_codes
FROM consultations
WHERE user_id = auth.uid()
  AND status = 'completed'
  AND transcript->>'confidence'::float > 0.5;
```

---

### Transcript History Table (Optional - for versioning)

```sql
CREATE TABLE transcript_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_id UUID NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    transcript JSONB NOT NULL, -- Full transcript data
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE transcript_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own transcript history"
    ON transcript_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE INDEX idx_transcript_history_consultation ON transcript_history(consultation_id);
CREATE INDEX idx_transcript_history_user ON transcript_history(user_id);
CREATE INDEX idx_transcript_history_created_at ON transcript_history(created_at DESC);
```

---

### Entity Cache Table (Redis Alternative)

**Note:** Use Redis for caching, or PostgreSQL table with TTL

```sql
CREATE TABLE entity_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transcript_hash VARCHAR(64) UNIQUE NOT NULL, -- SHA-256 hash
    entities JSONB NOT NULL,
    language VARCHAR(10),
    extraction_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL -- TTL
);

CREATE INDEX idx_entity_cache_hash ON entity_cache(transcript_hash);
CREATE INDEX idx_entity_cache_expires ON entity_cache(expires_at);

-- Cleanup expired entries (run via cron)
DELETE FROM entity_cache WHERE expires_at < NOW();
```

---

## 🔗 Relationships (Supabase)

### Entity Relationship Diagram

```
auth.users (Supabase Auth)
    │
    ├─> 1:1 User Profile
    │
    ├─> 1:1 Clinic Profile
    │
    ├─> 1:N Consultations (with RLS)
    │       │
    │       └─> Contains: transcript (JSONB), entities (JSONB), soap_note (JSONB)
    │
    ├─> 1:N Notes Index (for search)
    │
    ├─> 1:N Transcript History
    │
    └─> 1:N Audit Logs (with RLS)

Consultations (PostgreSQL JSONB)
    │
    ├─> Contains: transcript, entities, soap_note (all JSONB)
    ├─> References: audio_file_path (Supabase Storage)
    └─> References: pdf_url (Supabase Storage)
```

**Row Level Security (RLS):**
- All tables have RLS enabled
- Users can only access their own data
- Automatic DPDP compliance
- No manual permission checks needed

---

## 🔒 Data Encryption

### Encrypted Fields

**PostgreSQL:**
- `users.password_hash` - Already hashed (bcrypt)
- `users.email` - Can be encrypted if needed
- `consultations.patient_name` - Encrypted (AES-256)

**MongoDB:**
- `notes.patient_name` - Encrypted
- `notes.transcript.text` - Encrypted
- `notes.soap_note` - Encrypted

**Encryption Method:**
- Field-level encryption (AES-256)
- Encryption keys stored in environment variables
- Key rotation: Every 90 days

---

## 📊 Data Retention

### Retention Policies

**PostgreSQL:**
- Users: Indefinite (until account deletion)
- Consultations: 7 years (medical records)
- Audit Logs: 7 years
- API Usage: 1 year (for cost analysis)

**MongoDB:**
- Notes: 7 years
- Transcripts: 7 years
- Entities Cache: 5 minutes (TTL)

**Deletion:**
- Soft delete: `is_deleted` flag
- Hard delete: After 7 years + 30 days grace period
- Backup retention: 30 days

---

## 🚀 Migration Strategy

### Initial Migration

```sql
-- Migration: 001_initial_schema.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables in order
CREATE TABLE users (...);
CREATE TABLE consultations (...);
CREATE TABLE notes_metadata (...);
CREATE TABLE audit_logs (...);
CREATE TABLE api_usage (...);

-- Create indexes
-- (all indexes as shown above)

-- Create functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_consultations_updated_at BEFORE UPDATE ON consultations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notes_metadata_updated_at BEFORE UPDATE ON notes_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 📈 Performance Optimization

### Indexes Strategy

**PostgreSQL:**
- Primary keys: Automatic indexes
- Foreign keys: Indexed for joins
- Frequently queried fields: Indexed
- Composite indexes for common queries

**MongoDB:**
- `_id`: Automatic index
- Foreign key fields: Indexed
- Date fields: Indexed for sorting
- Text search: Full-text index on patient_name

### Query Optimization

**PostgreSQL:**
- Use EXPLAIN ANALYZE for slow queries
- Partition large tables (audit_logs)
- Connection pooling (PgBouncer)

**MongoDB:**
- Use projection to limit fields
- Pagination with skip/limit
- Aggregation pipeline for complex queries

---

## 🔄 Backup Strategy

### PostgreSQL Backup
- **Frequency:** Daily full backup
- **Retention:** 30 days
- **Method:** pg_dump + compression
- **Location:** S3 or local storage

### MongoDB Backup
- **Frequency:** Daily full backup
- **Retention:** 30 days
- **Method:** mongodump
- **Location:** S3 or local storage

### Recovery Testing
- Test restore monthly
- Document recovery procedures
- RTO: 4 hours
- RPO: 24 hours

---

## ✅ Next Steps

1. **Security Architecture** - Encryption details
2. **Integration Design** - External API integration
3. **Implementation** - Create migrations and models

---

**Document Status:** ✅ Complete  
**Ready for:** Security Architecture  
**Next Document:** `security-architecture.md`

---

**Last Updated:** November 29, 2024  
**Version:** 1.0

