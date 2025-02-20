from supabase import create_client, Client
import os

# Supabase credentials
SUPABASE_URL = "https://oqcfbhygzbrsehlsrflx.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9xY2ZiaHlnemJyc2VobHNyZmx4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MDA1MjgxMywiZXhwIjoyMDU1NjI4ODEzfQ.lW-QYFDctANqGDL1m7zu9ASyp_tabESt0YNRDywCsVs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_NAME = "mini-blog"

def upload_to_supabase(file):
    """
    Uploads a file to Supabase Storage and returns its public URL.
    
    :param file: File object from Flask request
    :return: (public_url, error) - Returns public URL if successful, else returns error
    """
    file_name = file.filename

    file_content = file.read()

    response = supabase.storage.from_(BUCKET_NAME).upload(file_name, file_content)

    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
    return public_url, None
