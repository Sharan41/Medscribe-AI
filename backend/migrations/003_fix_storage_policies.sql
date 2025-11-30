-- Fix Storage Bucket Policies
-- Allow authenticated users to upload files

-- Policy for INSERT (upload)
CREATE POLICY "Allow authenticated users to upload audio"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'audio-files'
);

-- Policy for SELECT (read/download)
CREATE POLICY "Allow public read audio files"
ON storage.objects FOR SELECT
TO public
USING (
  bucket_id = 'audio-files'
);

-- Policy for UPDATE (if needed)
CREATE POLICY "Allow authenticated users to update audio"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'audio-files'
)
WITH CHECK (
  bucket_id = 'audio-files'
);

-- Policy for DELETE (if needed)
CREATE POLICY "Allow authenticated users to delete audio"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'audio-files'
);

-- Same policies for 'notes' bucket
CREATE POLICY "Allow authenticated users to upload notes"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'notes'
);

CREATE POLICY "Allow public read notes"
ON storage.objects FOR SELECT
TO public
USING (
  bucket_id = 'notes'
);

