"""
Transcription Service
Handles audio transcription using AssemblyAI (primary) or Reverie API (fallback)
"""

from app.config import settings
from app.services.audio_converter import audio_converter
import logging
from typing import Optional, Dict, Any
import os
import tempfile

logger = logging.getLogger(__name__)

# Try to import AssemblyAI (primary service)
try:
    from app.services.assemblyai_service import assemblyai_service
    ASSEMBLYAI_AVAILABLE = True
except ImportError:
    ASSEMBLYAI_AVAILABLE = False
    logger.warning("AssemblyAI not available")

# Try to import Reverie SDK (optional, requires Python <3.13)
try:
    from reverie_sdk import ReverieClient
    REVERIE_AVAILABLE = True
except ImportError:
    REVERIE_AVAILABLE = False
    logger.info("Reverie SDK not available (requires Python <3.13). Using AssemblyAI as primary service.")
    ReverieClient = None

class TranscriptionService:
    """Service for transcribing audio files using AssemblyAI (primary) or Reverie API (fallback)"""
    
    def __init__(self):
        """Initialize transcription clients"""
        self.reverie_client = None
        if REVERIE_AVAILABLE and ReverieClient:
            try:
                self.reverie_client = ReverieClient(
                    api_key=settings.REVERIE_API_KEY,
                    app_id=settings.REVERIE_APP_ID,
                    verbose=False
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Reverie client: {e}")
                self.reverie_client = None
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str,
        audio_format: str = "mp3",
        enable_diarization: bool = True,
        use_assemblyai: bool = False  # Use AssemblyAI for better diarization (96% vs 85%)
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using Reverie API or AssemblyAI
        
        Args:
            audio_data: Binary audio file data
            language: Language code ("ta" for Tamil, "te" for Telugu)
            audio_format: Audio format ("mp3", "wav", etc.)
            enable_diarization: Enable speaker diarization to separate doctor/patient
            use_assemblyai: Use AssemblyAI instead of Reverie (better diarization, 96% accuracy)
        
        Returns:
            Dictionary with transcription results
        """
        # Use AssemblyAI if requested and available (or if Reverie not available)
        if (use_assemblyai or not REVERIE_AVAILABLE or not self.reverie_client) and ASSEMBLYAI_AVAILABLE:
            if enable_diarization:
                return await self._transcribe_with_assemblyai(audio_data, language, audio_format)
            else:
                # AssemblyAI without diarization
                return await self._transcribe_with_assemblyai(audio_data, language, audio_format)
        
        # Fallback to Reverie (only if available and not using AssemblyAI)
        if not REVERIE_AVAILABLE or not self.reverie_client:
            if ASSEMBLYAI_AVAILABLE:
                logger.info("Reverie not available, using AssemblyAI")
                return await self._transcribe_with_assemblyai(audio_data, language, audio_format)
            else:
                raise Exception("No transcription service available. Please configure AssemblyAI or Reverie.")
        
        try:
            logger.info(f"Starting transcription (language: {language}, format: {audio_format})")
            
            # Map language codes
            lang_map = {
                "ta": "ta",  # Tamil
                "te": "te",  # Telugu
                "hi": "hi"   # Hindi (if needed)
            }
            src_lang = lang_map.get(language, "ta")
            
            # Convert audio to Reverie-supported format if needed
            original_format = audio_format.lower()
            if original_format in ["webm", "ogg", "m4a"]:
                logger.info(f"🔄 Converting {original_format} to MP3 for Reverie API")
                try:
                    audio_data, converted_format = audio_converter.convert_for_reverie(
                        audio_data, original_format
                    )
                    audio_format = converted_format
                    logger.info(f"✅ Successfully converted {original_format} to {converted_format}")
                except Exception as conv_error:
                    logger.error(f"❌ Audio conversion failed: {str(conv_error)}", exc_info=True)
                    raise Exception(f"Failed to convert {original_format} audio. Please ensure ffmpeg is installed: {str(conv_error)}")
            
            # Determine format parameter for Reverie
            format_map = {
                "mp3": "mp3",
                "wav": "16k_int16",
                "m4a": "m4a"
            }
            reverie_format = format_map.get(audio_format.lower(), "mp3")
            
            # Call Reverie API
            # Note: speaker_diarization and punctuate may not be available in all SDK versions
            # Using minimal parameters that are definitely supported
            if not self.reverie_client:
                raise Exception("Reverie client not initialized")
            
            result = self.reverie_client.asr.stt_file(
                src_lang=src_lang,
                data=audio_data,
                format=reverie_format,
                logging="true"
            )
            
            # Extract transcript text
            transcript_text = result.text if hasattr(result, 'text') else str(result)
            confidence = getattr(result, 'confidence', 0.0)
            
            # Parse diarization results if available
            doctor_text = ""
            patient_text = ""
            segments = []
            
            if enable_diarization and hasattr(result, 'segments'):
                # Parse speaker-separated segments
                # Format: [{"speaker": "SPEAKER_00", "text": "...", "start": 0.0, "end": 5.2}, ...]
                segments = getattr(result, 'segments', [])
                
                # Separate doctor and patient speech
                # Assumption: First speaker is usually doctor, second is patient
                # This may need adjustment based on actual Reverie output format
                for segment in segments:
                    speaker = segment.get('speaker', '')
                    text = segment.get('text', '')
                    
                    if 'SPEAKER_00' in speaker or 'doctor' in speaker.lower():
                        doctor_text += text + " "
                    else:
                        patient_text += text + " "
            
            # Estimate audio duration (rough calculation)
            # This is approximate - actual duration may vary
            duration = len(audio_data) / 16000  # Rough estimate for 16kHz audio
            
            # Calculate cost (₹0.50 per minute)
            cost = (duration / 60) * settings.REVERIE_COST_PER_MINUTE
            
            logger.info(f"Transcription completed: {len(transcript_text)} characters, confidence: {confidence}")
            
            return {
                "text": transcript_text.strip(),
                "confidence": float(confidence) if confidence else 0.0,
                "segments": segments,
                "doctor_text": doctor_text.strip(),
                "patient_text": patient_text.strip(),
                "duration": duration,
                "cost": round(cost, 2),
                "language": language,
                "model": "reverie-asr"
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Transcription failed: {error_msg}", exc_info=True)
            print(f"\n{'='*60}")
            print(f"❌ TRANSCRIPTION ERROR")
            print(f"Error: {error_msg}")
            print(f"Type: {type(e).__name__}")
            print(f"{'='*60}\n")
            raise Exception(f"Transcription failed: {error_msg}")
    
    async def _transcribe_with_assemblyai(
        self,
        audio_data: bytes,
        language: str,
        audio_format: str = "mp3"
    ) -> Dict[str, Any]:
        """
        Transcribe using AssemblyAI with superior speaker diarization (96% accuracy)
        """
        try:
            # Save audio to temporary file for AssemblyAI
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                # Use AssemblyAI service
                result = await assemblyai_service.transcribe_with_diarization(
                    audio_url=tmp_path,
                    language=language
                )
                return result
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        except Exception as e:
            logger.error(f"AssemblyAI transcription failed: {e}", exc_info=True)
            raise
    
    def estimate_cost(self, audio_duration_seconds: float) -> float:
        """
        Estimate transcription cost
        
        Args:
            audio_duration_seconds: Audio duration in seconds
        
        Returns:
            Estimated cost in ₹
        """
        minutes = audio_duration_seconds / 60
        return round(minutes * settings.REVERIE_COST_PER_MINUTE, 2)

# Global service instance
transcription_service = TranscriptionService()

