"""
Audio Format Converter Service
Converts audio files to formats supported by transcription APIs
"""

import logging
from io import BytesIO
from typing import Tuple
from pydub import AudioSegment
import tempfile
import os

logger = logging.getLogger(__name__)


class AudioConverter:
    """Service for converting audio files to supported formats"""

    def __init__(self):
        logger.info("🔄 AudioConverter initialized")

    def convert_to_mp3(
        self,
        audio_data: bytes,
        source_format: str = "webm"
    ) -> Tuple[bytes, str]:
        """
        Convert audio file to MP3 format
        
        Args:
            audio_data: Binary audio file data
            source_format: Source format (webm, wav, m4a, etc.)
            
        Returns:
            Tuple of (converted_audio_bytes, file_extension)
        """
        try:
            logger.info(f"Converting audio from {source_format} to MP3")
            
            # Create temporary file for input
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{source_format}") as temp_input:
                temp_input.write(audio_data)
                temp_input_path = temp_input.name
            
            try:
                # Load audio file
                audio = AudioSegment.from_file(temp_input_path, format=source_format)
                
                # Export to MP3
                output_buffer = BytesIO()
                audio.export(output_buffer, format="mp3", bitrate="128k")
                output_buffer.seek(0)
                converted_data = output_buffer.read()
                
                logger.info(f"✅ Successfully converted {source_format} to MP3 ({len(converted_data)} bytes)")
                return converted_data, "mp3"
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_input_path):
                    os.unlink(temp_input_path)
                    
        except Exception as e:
            logger.error(f"❌ Audio conversion failed: {str(e)}", exc_info=True)
            raise Exception(f"Failed to convert audio from {source_format} to MP3: {str(e)}")

    def convert_to_wav(
        self,
        audio_data: bytes,
        source_format: str = "webm"
    ) -> Tuple[bytes, str]:
        """
        Convert audio file to WAV format (16kHz, 16-bit, mono for Reverie)
        
        Args:
            audio_data: Binary audio file data
            source_format: Source format (webm, mp3, m4a, etc.)
            
        Returns:
            Tuple of (converted_audio_bytes, file_extension)
        """
        try:
            logger.info(f"Converting audio from {source_format} to WAV")
            
            # Create temporary file for input
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{source_format}") as temp_input:
                temp_input.write(audio_data)
                temp_input_path = temp_input.name
            
            try:
                # Load audio file
                audio = AudioSegment.from_file(temp_input_path, format=source_format)
                
                # Convert to 16kHz, 16-bit, mono (Reverie format)
                audio = audio.set_frame_rate(16000)
                audio = audio.set_sample_width(2)  # 16-bit
                audio = audio.set_channels(1)  # Mono
                
                # Export to WAV
                output_buffer = BytesIO()
                audio.export(output_buffer, format="wav")
                output_buffer.seek(0)
                converted_data = output_buffer.read()
                
                logger.info(f"✅ Successfully converted {source_format} to WAV ({len(converted_data)} bytes)")
                return converted_data, "wav"
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_input_path):
                    os.unlink(temp_input_path)
                    
        except Exception as e:
            logger.error(f"❌ Audio conversion failed: {str(e)}", exc_info=True)
            raise Exception(f"Failed to convert audio from {source_format} to WAV: {str(e)}")

    def convert_for_reverie(
        self,
        audio_data: bytes,
        source_format: str
    ) -> Tuple[bytes, str]:
        """
        Convert audio to format best suited for Reverie API
        
        Args:
            audio_data: Binary audio file data
            source_format: Source format (webm, mp3, wav, etc.)
            
        Returns:
            Tuple of (converted_audio_bytes, target_format)
        """
        # Reverie prefers MP3 or 16kHz WAV
        # Convert WebM to MP3 for best compatibility
        if source_format.lower() in ["webm", "ogg", "m4a"]:
            return self.convert_to_mp3(audio_data, source_format)
        elif source_format.lower() == "wav":
            # Check if WAV is already in correct format, if not convert
            return self.convert_to_wav(audio_data, source_format)
        else:
            # MP3 or other formats - return as-is or convert to MP3
            if source_format.lower() != "mp3":
                return self.convert_to_mp3(audio_data, source_format)
            return audio_data, "mp3"


audio_converter = AudioConverter()

