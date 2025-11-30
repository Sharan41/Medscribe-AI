"""
User Management Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from app.database import get_supabase
from app.api.auth import get_current_user

router = APIRouter()

class UserUpdate(BaseModel):
    name: Optional[str] = None
    clinic_name: Optional[str] = None

class ClinicProfileUpdate(BaseModel):
    clinic_name: str
    address: Optional[str] = None
    license_no: Optional[str] = None
    doctor_reg: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

@router.get("/me")
async def get_current_user_profile(current_user: Any = Depends(get_current_user)):
    """
    Get current user profile
    """
    supabase = get_supabase()
    
    try:
        profile_response = supabase.table("user_profiles").select("*").eq("id", current_user.id).single().execute()
        
        return {
            "success": True,
            "user": profile_response.data
        }
    
    except Exception as e:
        raise HTTPException(status_code=404, detail="User profile not found")

@router.put("/me")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: Any = Depends(get_current_user)
):
    """
    Update user profile
    """
    supabase = get_supabase()
    
    try:
        update_data = {}
        if user_update.name:
            update_data["name"] = user_update.name
        
        if update_data:
            supabase.table("user_profiles").update(update_data).eq("id", current_user.id).execute()
        
        # Update clinic if provided
        if user_update.clinic_name:
            supabase.table("clinic_profiles").upsert({
                "user_id": current_user.id,
                "clinic_name": user_update.clinic_name
            }).execute()
        
        # Get updated profile
        profile_response = supabase.table("user_profiles").select("*").eq("id", current_user.id).single().execute()
        
        return {
            "success": True,
            "user": profile_response.data
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/me/clinic")
async def update_clinic_profile(
    clinic_update: ClinicProfileUpdate,
    current_user: Any = Depends(get_current_user)
):
    """
    Update clinic profile
    """
    supabase = get_supabase()
    
    try:
        clinic_data = {
            "user_id": current_user.id,
            "clinic_name": clinic_update.clinic_name,
            "address": clinic_update.address,
            "license_no": clinic_update.license_no,
            "doctor_reg": clinic_update.doctor_reg,
            "phone": clinic_update.phone,
            "email": clinic_update.email
        }
        
        # Remove None values
        clinic_data = {k: v for k, v in clinic_data.items() if v is not None}
        
        supabase.table("clinic_profiles").upsert(clinic_data).execute()
        
        clinic_response = supabase.table("clinic_profiles").select("*").eq("user_id", current_user.id).single().execute()
        
        return {
            "success": True,
            "clinic": clinic_response.data
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

