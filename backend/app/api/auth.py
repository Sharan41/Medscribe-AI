"""
Authentication Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import get_supabase
from app.config import settings

router = APIRouter()
security = HTTPBearer()

# Request Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    clinic_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    clinic_name: Optional[str] = None

@router.post("/register")
async def register(user_data: UserRegister):
    """
    Register a new user
    """
    supabase = get_supabase()
    
    try:
        # Create user in Supabase Auth
        # Note: Supabase validates email domains, so use a real email for testing
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "name": user_data.name,
                    "clinic_name": user_data.clinic_name
                }
            }
        })
        
        if auth_response.user is None:
            raise HTTPException(
                status_code=400, 
                detail="Registration failed. Please use a valid email address (Supabase validates email domains)."
            )
        
        user_id = auth_response.user.id
        
        # Create user profile
        try:
            profile_response = supabase.table("user_profiles").insert({
                "id": user_id,
                "email": user_data.email,
                "name": user_data.name
            }).execute()
        except Exception as profile_error:
            # Profile might already exist or table doesn't exist yet
            print(f"Profile creation warning: {profile_error}")
        
        # Create clinic profile if provided
        if user_data.clinic_name:
            try:
                supabase.table("clinic_profiles").insert({
                    "user_id": user_id,
                    "clinic_name": user_data.clinic_name
                }).execute()
            except Exception as clinic_error:
                print(f"Clinic profile creation warning: {clinic_error}")
        
        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": auth_response.user.email,
                "name": user_data.name
            },
            "message": "Registration successful. Please verify your email.",
            "session": auth_response.session.model_dump() if auth_response.session else None
        }
    
    except Exception as e:
        error_message = str(e)
        # Provide helpful error message for email validation
        if "invalid" in error_message.lower() or "email" in error_message.lower():
            error_message = f"Email validation failed: {error_message}. Note: Supabase validates email domains. Use a real email address for testing (e.g., Gmail, Outlook)."
        raise HTTPException(status_code=400, detail=error_message)

@router.post("/login")
async def login(credentials: UserLogin):
    """
    Login and get JWT token
    """
    supabase = get_supabase()
    
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if auth_response.user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if email is verified (if email verification is enabled)
        if auth_response.user.email_confirmed_at is None:
            raise HTTPException(
                status_code=403,
                detail="Email not verified. Please check your email and verify your account, or disable email verification in Supabase settings for development."
            )
        
        # Get user profile (handle case where profile doesn't exist yet)
        try:
            profile_response = supabase.table("user_profiles").select("*").eq("id", auth_response.user.id).single().execute()
            user_name = profile_response.data.get("name", "") if profile_response.data else ""
        except Exception:
            # Profile doesn't exist yet, use metadata
            user_name = auth_response.user.user_metadata.get("name", "")
        
        if not auth_response.session:
            raise HTTPException(status_code=401, detail="Login failed: No session created")
        
        return {
            "success": True,
            "token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "name": user_name,
            },
            "expires_in": auth_response.session.expires_in
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "email" in error_msg.lower() or "verify" in error_msg.lower():
            raise HTTPException(
                status_code=403,
                detail="Email verification required. Please verify your email or disable email verification in Supabase Dashboard → Authentication → Settings."
            )
        raise HTTPException(status_code=401, detail=f"Login failed: {error_msg}")

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token
    """
    supabase = get_supabase()
    
    try:
        auth_response = supabase.auth.refresh_session(refresh_token)
        
        return {
            "success": True,
            "token": auth_response.session.access_token,
            "expires_in": auth_response.session.expires_in
        }
    
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current authenticated user
    """
    supabase = get_supabase()
    token = credentials.credentials
    
    try:
        # Verify token and get user
        user_response = supabase.auth.get_user(token)
        
        if user_response.user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_response.user
    
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user_and_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current authenticated user and their JWT token
    Returns tuple: (user, token)
    """
    supabase = get_supabase()
    token = credentials.credentials
    
    try:
        # Verify token and get user
        user_response = supabase.auth.get_user(token)
        
        if user_response.user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_response.user, token
    
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

