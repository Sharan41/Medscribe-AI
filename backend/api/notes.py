"""
FastAPI endpoints for SOAP note generation
"""

from fastapi import APIRouter, HTTPException
from services.soap_generator import SOAPGenerator, TranscriptRequest
from typing import Optional
import os

router = APIRouter(prefix="/notes", tags=["notes"])
generator = SOAPGenerator()

@router.post("/generate")
async def generate_soap_note(request: TranscriptRequest):
    """
    Generate SOAP note from transcript using LLM
    
    Example request:
    {
        "transcript": "நோயாளிக்கு காய்ச்சல் உள்ளது. BP 120/80.",
        "language": "ta",
        "patient_name": "Patient Name",
        "doctor_name": "Dr. Priya"
    }
    """
    try:
        # Generate SOAP note
        result = generator.generate_soap_note(request)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail="Failed to generate SOAP note. Please try again."
            )
        
        # TODO: Save to database
        # note = Note(...)
        # db.save_note(note)
        
        return {
            "success": True,
            "soap_note": result["soap_note"],
            "patient_name": result["patient_name"],
            "doctor_name": result["doctor_name"],
            "date": result["date"],
            "language": result["language"],
            "message": "SOAP note generated successfully"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SOAP note: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "SOAP Note Generator",
        "llm_provider": "Groq"
    }

