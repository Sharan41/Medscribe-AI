-- Migration: Add Review/Edit Workflow Support
-- Adds review status, approval tracking, and edit history

-- Step 1: Update status enum to include 'review' status
ALTER TABLE consultations 
DROP CONSTRAINT IF EXISTS consultations_status_check;

ALTER TABLE consultations
ADD CONSTRAINT consultations_status_check 
CHECK (status IN ('processing', 'review', 'completed', 'failed'));

-- Step 2: Add review and approval tracking fields
ALTER TABLE consultations
ADD COLUMN IF NOT EXISTS review_status VARCHAR(50) DEFAULT NULL CHECK (review_status IN ('pending_review', 'under_review', 'approved', 'rejected')),
ADD COLUMN IF NOT EXISTS reviewed_by UUID REFERENCES auth.users(id),
ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES auth.users(id),
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS review_notes TEXT,
ADD COLUMN IF NOT EXISTS edit_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_edited_by UUID REFERENCES auth.users(id),
ADD COLUMN IF NOT EXISTS last_edited_at TIMESTAMP;

-- Step 3: Add edit history table for tracking changes
CREATE TABLE IF NOT EXISTS consultation_edit_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consultation_id UUID NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
    edited_by UUID NOT NULL REFERENCES auth.users(id),
    field_name VARCHAR(100) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    edit_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security for edit history
ALTER TABLE consultation_edit_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view edit history for own consultations"
    ON consultation_edit_history FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM consultations 
            WHERE consultations.id = consultation_edit_history.consultation_id 
            AND consultations.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert edit history for own consultations"
    ON consultation_edit_history FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM consultations 
            WHERE consultations.id = consultation_edit_history.consultation_id 
            AND consultations.user_id = auth.uid()
        )
    );

-- Indexes
CREATE INDEX IF NOT EXISTS idx_consultation_edit_history_consultation_id 
    ON consultation_edit_history(consultation_id);
CREATE INDEX IF NOT EXISTS idx_consultation_edit_history_edited_by 
    ON consultation_edit_history(edited_by);
CREATE INDEX IF NOT EXISTS idx_consultation_edit_history_created_at 
    ON consultation_edit_history(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_consultations_review_status 
    ON consultations(review_status);
CREATE INDEX IF NOT EXISTS idx_consultations_reviewed_by 
    ON consultations(reviewed_by);
CREATE INDEX IF NOT EXISTS idx_consultations_approved_by 
    ON consultations(approved_by);

-- Step 4: Update audit log function to track review/approval actions
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
        COALESCE(NEW.reviewed_by, NEW.approved_by, NEW.user_id),
        CASE 
            WHEN TG_OP = 'INSERT' THEN 'create'
            WHEN TG_OP = 'UPDATE' THEN 
                CASE
                    WHEN NEW.review_status = 'approved' AND (OLD.review_status IS NULL OR OLD.review_status != 'approved') THEN 'approve'
                    WHEN NEW.review_status = 'under_review' AND (OLD.review_status IS NULL OR OLD.review_status != 'under_review') THEN 'review'
                    WHEN NEW.edit_count > OLD.edit_count THEN 'update'
                    ELSE 'update'
                END
            WHEN TG_OP = 'DELETE' THEN 'delete'
        END,
        'consultation',
        NEW.id,
        jsonb_build_object(
            'patient_name', NEW.patient_name,
            'language', NEW.language,
            'status', NEW.status,
            'review_status', NEW.review_status,
            'reviewed_by', NEW.reviewed_by,
            'approved_by', NEW.approved_by,
            'edit_count', NEW.edit_count
        ),
        NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 5: Function to automatically set status to 'review' when SOAP note is generated
CREATE OR REPLACE FUNCTION set_review_status_on_soap_completion()
RETURNS TRIGGER AS $$
BEGIN
    -- When SOAP note is added and status changes to 'completed', set to 'review' instead
    IF NEW.soap_note IS NOT NULL 
       AND OLD.soap_note IS NULL 
       AND NEW.status = 'completed' THEN
        NEW.status = 'review';
        NEW.review_status = 'pending_review';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_review_status_trigger
    BEFORE UPDATE ON consultations
    FOR EACH ROW
    WHEN (NEW.soap_note IS NOT NULL AND OLD.soap_note IS NULL)
    EXECUTE FUNCTION set_review_status_on_soap_completion();

COMMENT ON COLUMN consultations.review_status IS 'Status of review workflow: pending_review, under_review, approved, rejected';
COMMENT ON COLUMN consultations.reviewed_by IS 'User ID who reviewed the consultation';
COMMENT ON COLUMN consultations.approved_by IS 'User ID who approved the consultation';
COMMENT ON COLUMN consultations.edit_count IS 'Number of times the consultation has been edited';
COMMENT ON COLUMN consultations.last_edited_by IS 'User ID who last edited the consultation';

