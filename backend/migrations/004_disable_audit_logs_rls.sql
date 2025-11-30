-- Disable RLS on audit_logs table
-- Audit logs are system logs, safe to disable RLS for server-side operations

ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;

-- Note: If you want to keep RLS enabled, you can create policies instead:
-- CREATE POLICY "Allow service role to insert audit logs"
-- ON audit_logs FOR INSERT
-- TO service_role
-- WITH CHECK (true);

