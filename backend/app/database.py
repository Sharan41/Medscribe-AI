"""
Supabase Database Client
"""

from supabase import create_client, Client
from app.config import settings
from typing import Optional

# Global Supabase client (anon key - for public operations)
supabase_client: Optional[Client] = None

def get_supabase() -> Client:
    """Get Supabase client instance (uses anon key - for public operations)"""
    global supabase_client
    
    if supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("Supabase URL and KEY must be set in environment variables")
        
        supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    return supabase_client

def get_supabase_with_token(token: str) -> Client:
    """
    Get Supabase client with user's JWT token (for RLS policies)
    
    Args:
        token: User's JWT token from authentication
    
    Returns:
        Supabase client authenticated with user's token
    """
    if not settings.SUPABASE_URL:
        raise ValueError("Supabase URL must be set in environment variables")
    
    # Create client with anon key
    client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )
    
    # Set the Authorization header for RLS policies
    # The postgrest client uses this header to identify the user
    if hasattr(client, 'postgrest') and hasattr(client.postgrest, 'session'):
        client.postgrest.session.headers['Authorization'] = f"Bearer {token}"
        client.postgrest.session.headers['apikey'] = settings.SUPABASE_KEY
    
    return client

def get_supabase_service() -> Client:
    """Get Supabase client with service role (for admin operations, bypasses RLS)"""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise ValueError("Supabase URL and SERVICE_KEY must be set")
    
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )

