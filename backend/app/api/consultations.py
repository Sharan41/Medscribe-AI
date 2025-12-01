"""
Consultation Endpoints
Unified endpoint for audio upload + transcription + SOAP generation
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Literal
from app.database import get_supabase, get_supabase_service
from app.api.auth import get_current_user
from app.config import settings
from app.services.transcription_service import transcription_service
from app.services.soap_service import soap_service
# PDF service imported lazily to avoid startup errors if WeasyPrint dependencies missing
import uuid
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ConsultationResponse(BaseModel):
    id: str
    status: Literal["processing", "completed", "failed"]
    patient_name: Optional[str] = None
    language: str
    websocket_url: Optional[str] = None
    poll_url: str
    estimated_time: Optional[int] = None
    created_at: str

def process_consultation_background(
    consultation_id: str,
    audio_data: bytes,
    language: str,
    audio_format: str,
    patient_name: Optional[str]
):
    """
    Background task to process consultation:
    1. Transcribe audio
    2. Generate SOAP note
    3. Update consultation record
    
    Note: This runs in a background thread, so we create a new event loop for async operations
    """
    logger.info(f"🚀 Background task started for consultation {consultation_id}")
    
    async def _process():
        # Use service role key for database operations (bypasses RLS)
        # Safe because we're updating records that belong to authenticated users
        supabase = get_supabase_service()
        
        try:
            logger.info(f"📝 Starting transcription for consultation {consultation_id}")
            # Update progress: transcription started
            supabase.table("consultations").update({
                "progress": {
                    "transcription": "processing",
                    "entity_extraction": "pending",
                    "soap_generation": "pending",
                    "pdf_generation": "pending"
                }
            }).eq("id", consultation_id).execute()
            
            # Step 1: Transcribe audio
            logger.info(f"🎤 Calling Reverie API for transcription (language: {language})")
            transcription_result = await transcription_service.transcribe_audio(
                audio_data=audio_data,
                language=language,
                audio_format=audio_format,
                enable_diarization=True
            )
            
            logger.info(f"✅ Transcription completed: {len(transcription_result.get('text', ''))} characters")
            
            transcript = transcription_result["text"]
            doctor_text = transcription_result.get("doctor_text", "")
            patient_text = transcription_result.get("patient_text", "")
            transcription_cost = transcription_result.get("cost", 0.0)
            
            # Update progress: transcription completed, SOAP generation started
            logger.info(f"💾 Updating consultation with transcript")
            # Note: transcription_cost column doesn't exist in schema, storing in cost field instead
            supabase.table("consultations").update({
                "transcript": transcript,
                "cost": transcription_cost,  # Store transcription cost in cost field
                "progress": {
                    "transcription": "completed",
                    "entity_extraction": "processing",
                    "soap_generation": "processing",
                    "pdf_generation": "pending"
                }
            }).eq("id", consultation_id).execute()
            
            # Step 2: Generate SOAP note
            logger.info(f"📋 Generating SOAP note with Groq LLM")
            soap_result = await soap_service.generate_soap_note(
                transcript=transcript,
                language=language,
                patient_name=patient_name,
                doctor_text=doctor_text if doctor_text else None,
                patient_text=patient_text if patient_text else None
            )
            
            logger.info(f"✅ SOAP note generated: {len(soap_result.get('soap_note', ''))} characters")
            
            soap_note = soap_result["soap_note"]
            entities = soap_result.get("entities", {})
            icd_codes = soap_result.get("icd_codes", [])
            
            # Calculate total cost (transcription + SOAP generation)
            total_cost = transcription_cost + soap_result.get("cost", 0.01)
            
            # Update consultation with results
            # Note: cost column exists, but subjective/objective/assessment/plan might not
            update_data = {
                "soap_note": soap_note,
                "entities": entities,
                "icd_codes": icd_codes,
                "cost": total_cost,
                "status": "completed",
                "progress": {
                    "transcription": "completed",
                    "entity_extraction": "completed",
                    "soap_generation": "completed",
                    "pdf_generation": "pending"
                },
                "completed_at": datetime.now().isoformat()
            }
            
            # Only add fields that exist in schema (soap_note is JSONB, can store structured data)
            # Store SOAP sections in soap_note JSONB field
            if isinstance(soap_note, str):
                # If soap_note is a string, convert to structured JSONB
                update_data["soap_note"] = {
                    "markdown": soap_note,
                    "subjective": soap_result.get("subjective", ""),
                    "objective": soap_result.get("objective", ""),
                    "assessment": soap_result.get("assessment", ""),
                    "plan": soap_result.get("plan", "")
                }
            else:
                update_data["soap_note"] = soap_note
            
            supabase.table("consultations").update(update_data).eq("id", consultation_id).execute()
            
        except Exception as e:
            # Update consultation with error
            error_msg = str(e)
            logger.error(f"❌ Background task failed for consultation {consultation_id}: {error_msg}", exc_info=True)
            print(f"\n{'='*60}")
            print(f"❌ ERROR in background task for consultation {consultation_id}")
            print(f"Error: {error_msg}")
            print(f"Error type: {type(e).__name__}")
            print(f"{'='*60}\n")
            try:
                supabase = get_supabase_service()
                # Note: error_message column doesn't exist in schema, using status only
                supabase.table("consultations").update({
                    "status": "failed"
                }).eq("id", consultation_id).execute()
            except Exception as update_error:
                logger.error(f"Failed to update consultation status to failed: {update_error}")
            # Log error details for debugging
            logger.error(f"Error details: {error_msg}")
            raise
    
    # Run async function in background thread with proper event loop handling
    # This works better on Render than asyncio.run()
    try:
        # Create a new event loop for this thread (required for background tasks)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_process())
            logger.info(f"✅ Background task completed for consultation {consultation_id}")
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"❌ Background task exception for consultation {consultation_id}: {str(e)}", exc_info=True)
        # Try to update status to failed even if event loop failed
        try:
            supabase = get_supabase_service()
            supabase.table("consultations").update({
                "status": "failed"
            }).eq("id", consultation_id).execute()
        except:
            pass
        raise

@router.post("", response_model=ConsultationResponse)
async def create_consultation(
    file: UploadFile = File(...),
    language: str = Form(..., description="Language code: 'ta' (Tamil) or 'te' (Telugu)"),
    patient_name: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user = Depends(get_current_user)
):
    """
    Upload audio file and start consultation processing pipeline
    
    This unified endpoint:
    1. Uploads audio file to Supabase Storage
    2. Creates consultation record
    3. Queues background processing (transcription + SOAP generation)
    4. Returns consultation ID for polling/WebSocket
    
    Processing happens asynchronously:
    - Transcription (Reverie API)
    - Entity extraction (Groq LLM)
    - SOAP note generation (Groq LLM)
    - PDF generation (WeasyPrint)
    """
    # Use service role key for database operations
    # We've already validated the user via get_current_user dependency
    # Service role bypasses RLS, which is safe since we're checking user_id matches
    supabase = get_supabase_service()
    
    # Validate file
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")
    
    # Check file type (allow WebM for browser recordings)
    allowed_types = settings.ALLOWED_FILE_TYPES
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file.content_type not in allowed_types and file_extension not in ['mp3', 'wav', 'webm']:
        raise HTTPException(status_code=400, detail="Invalid file type. Use MP3, WAV, or WebM.")
    
    # Validate language
    if language not in ["ta", "te"]:
        raise HTTPException(status_code=400, detail="Language must be 'ta' (Tamil) or 'te' (Telugu)")
    
    try:
        # Read audio file
        audio_data = await file.read()
        file_size = len(audio_data)
        
        # Generate unique file name
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'mp3'
        file_name = f"{uuid.uuid4()}.{file_extension}"
        storage_path = f"audio-files/{file_name}"
        
        # Upload to Supabase Storage
        try:
            storage_response = supabase.storage.from_("audio-files").upload(
                storage_path,
                audio_data,
                file_options={"content-type": file.content_type}
            )
            # Storage upload returns a Response object, check for errors differently
            if hasattr(storage_response, 'error') and storage_response.error:
                raise HTTPException(status_code=500, detail=f"Failed to upload audio file: {storage_response.error}")
        except Exception as storage_error:
            raise HTTPException(status_code=500, detail=f"Storage upload failed: {str(storage_error)}")
        
        # Get public URL
        public_url = supabase.storage.from_("audio-files").get_public_url(storage_path)
        
        # Create consultation record
        consultation_id = str(uuid.uuid4())
        consultation_data = {
            "id": consultation_id,
            "user_id": current_user.id,
            "patient_name": patient_name,
            "language": language,
            "audio_file_path": storage_path,
            "audio_file_size": file_size,
            "audio_format": file_extension,
            "status": "processing",
            "progress": {
                "transcription": "pending",
                "entity_extraction": "pending",
                "soap_generation": "pending",
                "pdf_generation": "pending"
            },
            "created_at": datetime.now().isoformat()
        }
        
        # Insert consultation record
        try:
            consultation_response = supabase.table("consultations").insert(consultation_data).execute()
            
            if not consultation_response.data:
                raise HTTPException(status_code=500, detail="Failed to create consultation: No data returned")
        except Exception as db_error:
            # Provide more detailed error message
            error_msg = str(db_error)
            if "row-level security" in error_msg.lower() or "RLS" in error_msg:
                raise HTTPException(
                    status_code=500, 
                    detail=f"RLS policy error (RLS should be disabled): {error_msg}. Please check Supabase dashboard."
                )
            raise HTTPException(status_code=500, detail=f"Database insert failed: {error_msg}")
        
        # Process consultation in background
        # For now, we'll process synchronously but return immediately
        # In production, use Supabase Edge Functions or Celery
        background_tasks.add_task(
            process_consultation_background,
            consultation_id=consultation_id,
            audio_data=audio_data,
            language=language,
            audio_format=file_extension,
            patient_name=patient_name
        )
        
        return ConsultationResponse(
            id=consultation_id,
            status="processing",
            patient_name=patient_name,
            language=language,
            websocket_url=f"wss://api.medscribe.ai/ws/{consultation_id}",  # TODO: Implement WebSocket
            poll_url=f"/consultations/{consultation_id}",
            estimated_time=45,  # Estimated seconds
            created_at=consultation_data["created_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create consultation: {str(e)}")

@router.get("", response_model=dict)
async def list_consultations(
    current_user = Depends(get_current_user),
    status: Optional[str] = None,
    limit: int = 50
):
    """
    List all consultations for the current user
    
    Query parameters:
    - status: Filter by status ('processing', 'completed', 'failed')
    - limit: Maximum number of results (default: 50)
    """
    supabase = get_supabase_service()
    
    try:
        query = supabase.table("consultations")\
            .select("*")\
            .eq("user_id", current_user.id)\
            .order("created_at", desc=True)\
            .limit(limit)
        
        if status:
            query = query.eq("status", status)
        
        response = query.execute()
        
        return {
            "consultations": response.data,
            "count": len(response.data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list consultations: {str(e)}")

@router.get("/{consultation_id}")
async def get_consultation(
    consultation_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get consultation status and results
    
    Use this endpoint to poll for completion.
    Poll every 2 seconds until status is "completed" or "failed".
    """
    # Use service role to bypass RLS (we've already validated user via get_current_user)
    supabase = get_supabase_service()
    
    try:
        consultation_response = supabase.table("consultations")\
            .select("*")\
            .eq("id", consultation_id)\
            .eq("user_id", current_user.id)\
            .single()\
            .execute()
        
        if not consultation_response.data:
            raise HTTPException(status_code=404, detail="Consultation not found")
        
        consultation = consultation_response.data
        
        # Format response based on status
        if consultation["status"] == "completed":
            return {
                "id": consultation["id"],
                "status": "completed",
                "patient_name": consultation.get("patient_name"),
                "language": consultation["language"],
                "transcript": consultation.get("transcript"),
                "entities": consultation.get("entities", []),
                "soap_note": consultation.get("soap_note"),
                "pdf_url": consultation.get("pdf_url"),
                "icd_codes": consultation.get("icd_codes", []),
                "cost": float(consultation.get("cost", 0)),
                "created_at": consultation["created_at"],
                "completed_at": consultation.get("completed_at")
            }
        elif consultation["status"] == "failed":
            # Consultation processing failed
            return {
                "id": consultation["id"],
                "status": consultation["status"],
                "patient_name": consultation.get("patient_name"),
                "language": consultation["language"],
                "error_message": consultation.get("error_message"),
                "created_at": consultation["created_at"]
            }
        else:
            # Still processing
            return {
                "id": consultation["id"],
                "status": consultation["status"],
                "progress": consultation.get("progress", {}),
                "estimated_time_remaining": 30,  # TODO: Calculate based on progress
                "created_at": consultation["created_at"]
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get consultation: {str(e)}")

@router.get("/{consultation_id}/pdf")
async def get_consultation_pdf(
    consultation_id: str,
    current_user = Depends(get_current_user)
):
    """
    Generate and download PDF for a consultation
    
    Returns PDF file with transcript, SOAP note, and extracted entities.
    """
    supabase = get_supabase()
    
    try:
        # Fetch consultation
        consultation_response = supabase.table("consultations")\
            .select("*")\
            .eq("id", consultation_id)\
            .eq("user_id", current_user.id)\
            .single()\
            .execute()
        
        if not consultation_response.data:
            raise HTTPException(status_code=404, detail="Consultation not found")
        
        consultation = consultation_response.data
        
        # Check if consultation is completed
        if consultation.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail="PDF can only be generated for completed consultations"
            )
        
        # Generate PDF (lazy import to avoid startup errors)
        try:
            # Set library paths before importing
            import os
            os.environ.setdefault('DYLD_LIBRARY_PATH', '/usr/local/lib')
            os.environ.setdefault('PKG_CONFIG_PATH', '/usr/local/lib/pkgconfig')
            
            from app.services.pdf_service import pdf_service
            pdf_bytes = pdf_service.generate_consultation_pdf(consultation)
        except (ImportError, OSError, Exception) as e:
            error_msg = str(e)
            logger.error(f"PDF generation failed: {error_msg}", exc_info=True)
            # Provide helpful error message
            if "libgobject" in error_msg.lower() or "gobject" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail="PDF generation unavailable. Please restart backend server using START_SERVER_WITH_PDF.sh script to set library paths, or set DYLD_LIBRARY_PATH=/usr/local/lib manually."
                )
            raise HTTPException(
                status_code=503,
                detail=f"PDF generation unavailable. Error: {error_msg[:200]}"
            )
        
        # Return PDF as response
        patient_name = consultation.get("patient_name", "consultation")
        filename = f"consultation_{patient_name}_{consultation_id[:8]}.pdf"
        
        return Response(
            content=pdf_bytes.read(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate PDF for consultation {consultation_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

