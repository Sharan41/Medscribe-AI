-- Migration: Add 'approve' and 'review' actions to audit_logs table
-- This allows the review workflow to properly log approval and review actions

-- Step 1: Drop the existing check constraint
ALTER TABLE audit_logs 
DROP CONSTRAINT IF EXISTS audit_logs_action_check;

-- Step 2: Add the updated constraint with 'approve' and 'review' actions
ALTER TABLE audit_logs
ADD CONSTRAINT audit_logs_action_check 
CHECK (action IN ('create', 'read', 'update', 'delete', 'login', 'logout', 'export', 'download', 'approve', 'review'));

COMMENT ON CONSTRAINT audit_logs_action_check ON audit_logs IS 'Allowed actions including review workflow actions: approve, review';

