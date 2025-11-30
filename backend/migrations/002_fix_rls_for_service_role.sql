-- Fix RLS policies to allow service role operations
-- Service role key bypasses RLS, but we need to ensure policies don't block it

-- Drop existing policies
DROP POLICY IF EXISTS "Users can create own consultations" ON consultations;
DROP POLICY IF EXISTS "Users can update own consultations" ON consultations;

-- Create new policies that allow service role operations
-- Service role has 'service_role' role which bypasses RLS, but we add explicit checks

CREATE POLICY "Users can create own consultations"
    ON consultations FOR INSERT
    WITH CHECK (
        -- Allow if user_id matches authenticated user
        auth.uid() = user_id
        OR
        -- Allow service role (bypasses RLS anyway, but explicit for clarity)
        auth.role() = 'service_role'
    );

CREATE POLICY "Users can update own consultations"
    ON consultations FOR UPDATE
    USING (
        -- Allow if user_id matches authenticated user
        auth.uid() = user_id
        OR
        -- Allow service role
        auth.role() = 'service_role'
    );

-- Also update other policies for consistency
DROP POLICY IF EXISTS "Users can view own consultations" ON consultations;
DROP POLICY IF EXISTS "Users can delete own consultations" ON consultations;

CREATE POLICY "Users can view own consultations"
    ON consultations FOR SELECT
    USING (
        auth.uid() = user_id
        OR
        auth.role() = 'service_role'
    );

CREATE POLICY "Users can delete own consultations"
    ON consultations FOR DELETE
    USING (
        auth.uid() = user_id
        OR
        auth.role() = 'service_role'
    );

