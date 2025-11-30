-- MedScribe AI Database Schema
-- Supabase PostgreSQL Migration
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USER PROFILES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    backup_codes TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security for user_profiles
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON user_profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_active ON user_profiles(is_active);

-- ============================================
-- CLINIC PROFILES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS clinic_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    clinic_name VARCHAR(255) NOT NULL,
    address TEXT,
    license_no VARCHAR(100),
    doctor_reg VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    monthly_budget DECIMAL(10, 2) DEFAULT 5000.00,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security for clinic_profiles
ALTER TABLE clinic_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own clinic"
    ON clinic_profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own clinic"
    ON clinic_profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own clinic"
    ON clinic_profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_clinic_profiles_user_id ON clinic_profiles(user_id);

-- ============================================
-- CONSULTATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS consultations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    patient_name VARCHAR(255),
    language VARCHAR(10) NOT NULL CHECK (language IN ('ta', 'te', 'hi')),
    
    -- Audio File
    audio_file_path VARCHAR(500),
    audio_file_size BIGINT,
    audio_duration INTEGER,
    audio_format VARCHAR(10),
    
    -- Processing Status
    status VARCHAR(50) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed')),
    progress JSONB DEFAULT '{}',
    
    -- Transcript (JSONB - flexible)
    transcript JSONB,
    
    -- Entities (JSONB array)
    entities JSONB DEFAULT '[]',
    
    -- SOAP Note (JSONB - flexible structure)
    soap_note JSONB,
    
    -- Additional Data
    icd_codes TEXT[],
    pdf_url VARCHAR(500),
    fhir_bundle JSONB,
    
    -- Metadata
    generation_method VARCHAR(50),
    generation_time FLOAT,
    cost DECIMAL(10, 4),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    CONSTRAINT valid_duration CHECK (audio_duration > 0 AND audio_duration <= 1800)
);

-- Row Level Security for consultations
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
CREATE INDEX IF NOT EXISTS idx_consultations_user_id ON consultations(user_id);
CREATE INDEX IF NOT EXISTS idx_consultations_status ON consultations(status);
CREATE INDEX IF NOT EXISTS idx_consultations_created_at ON consultations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_consultations_language ON consultations(language);

-- JSONB Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_consultations_transcript ON consultations USING GIN (transcript);
CREATE INDEX IF NOT EXISTS idx_consultations_soap_note ON consultations USING GIN (soap_note);
CREATE INDEX IF NOT EXISTS idx_consultations_entities ON consultations USING GIN (entities);

-- ============================================
-- NOTES INDEX TABLE (for search)
-- ============================================
CREATE TABLE IF NOT EXISTS notes_index (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consultation_id UUID NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    patient_name VARCHAR(255),
    title VARCHAR(255),
    language VARCHAR(10) NOT NULL CHECK (language IN ('ta', 'te', 'hi')),
    search_text TSVECTOR,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security for notes_index
ALTER TABLE notes_index ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own notes"
    ON notes_index FOR SELECT
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_notes_search_text ON notes_index USING GIN (search_text);
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes_index(user_id);
CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes_index(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notes_language ON notes_index(language);

-- ============================================
-- AUDIT LOGS TABLE (DPDP Compliance)
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    action VARCHAR(100) NOT NULL CHECK (action IN ('create', 'read', 'update', 'delete', 'login', 'logout', 'export', 'download')),
    resource_type VARCHAR(50) CHECK (resource_type IN ('note', 'consultation', 'user', 'audio', 'pdf', 'fhir')),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    request_id UUID,
    clinic_id UUID,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security for audit_logs
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own audit logs"
    ON audit_logs FOR SELECT
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_request_id ON audit_logs(request_id);

-- ============================================
-- API USAGE TRACKING TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    service VARCHAR(50) NOT NULL CHECK (service IN ('reverie', 'groq', 'huggingface')),
    endpoint VARCHAR(255),
    request_size BIGINT,
    response_size BIGINT,
    duration_ms INTEGER,
    cost DECIMAL(10, 4),
    status_code INTEGER,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security for api_usage
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own api usage"
    ON api_usage FOR SELECT
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_service ON api_usage(service);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_cost ON api_usage(service, created_at DESC);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clinic_profiles_updated_at 
    BEFORE UPDATE ON clinic_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_consultations_updated_at 
    BEFORE UPDATE ON consultations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notes_index_updated_at 
    BEFORE UPDATE ON notes_index
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update search_text in notes_index
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

-- Function to auto-create audit log on consultation changes
CREATE OR REPLACE FUNCTION log_consultation_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action,
        resource_type,
        resource_id,
        details,
        created_at
    ) VALUES (
        NEW.user_id,
        CASE 
            WHEN TG_OP = 'INSERT' THEN 'create'
            WHEN TG_OP = 'UPDATE' THEN 'update'
            WHEN TG_OP = 'DELETE' THEN 'delete'
        END,
        'consultation',
        NEW.id,
        jsonb_build_object(
            'patient_name', NEW.patient_name,
            'language', NEW.language,
            'status', NEW.status
        ),
        NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_consultation_changes
    AFTER INSERT OR UPDATE OR DELETE ON consultations
    FOR EACH ROW EXECUTE FUNCTION log_consultation_changes();

-- ============================================
-- STORAGE BUCKETS (Run in Supabase Dashboard)
-- ============================================
-- Note: Create these buckets in Supabase Dashboard > Storage
-- 1. audio-files (public access)
-- 2. notes (public access for PDFs)

