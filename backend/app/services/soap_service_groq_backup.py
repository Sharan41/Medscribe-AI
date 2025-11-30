"""
SOAP Generation Service
Generates structured SOAP notes from transcripts using Groq LLM
"""

import groq
from app.config import settings
import logging
from typing import Dict, Any, Optional
import json
import re

logger = logging.getLogger(__name__)

class SOAPGenerationService:
    """Service for generating SOAP notes using Groq LLM"""
    
    def __init__(self):
        """Initialize Groq client"""
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        # Model selection with fallback support
        # Primary: llama-3.1-8b-instant (fast, reliable, currently available)
        # Fallback: mixtral-8x7b-32768 (alternative if primary unavailable)
        # Note: llama-3.1-70b-versatile was decommissioned
        # Using 8b-instant as primary for reliability, can upgrade to larger model later
        self.model = "llama-3.1-8b-instant"
        self.fallback_model = "mixtral-8x7b-32768"
    
    async def generate_soap_note(
        self,
        transcript: str,
        language: str,
        patient_name: Optional[str] = None,
        doctor_text: Optional[str] = None,
        patient_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured SOAP note from transcript
        
        Args:
            transcript: Full transcript text
            language: Language code ("ta" for Tamil, "te" for Telugu)
            patient_name: Patient name (optional)
            doctor_text: Doctor's speech only (if diarization available)
            patient_text: Patient's speech only (if diarization available)
        
        Returns:
            Dictionary with SOAP note and extracted entities:
            {
                "soap_note": str,  # Markdown-formatted SOAP note
                "subjective": str,
                "objective": str,
                "assessment": str,
                "plan": str,
                "entities": {
                    "symptoms": list,
                    "medications": list,
                    "diagnoses": list,
                    "vitals": dict
                },
                "icd_codes": list,  # ICD-10 codes
                "confidence": float,
                "model": str
            }
        """
        try:
            logger.info(f"Generating SOAP note (language: {language})")
            
            # Build enhanced prompt with diarization info if available
            context = ""
            if doctor_text and patient_text:
                context = f"""
Doctor's Speech:
{doctor_text}

Patient's Speech:
{patient_text}
"""
            else:
                context = f"Full Transcript:\n{transcript}"
            
            # Professional medical scribe prompt based on industry standards
            lang_name = "Tamil" if language == "ta" else "Telugu"
            
            prompt = self._create_professional_prompt(transcript, language, lang_name, context)
            
            # Call Groq API with fallback model support
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            api_params = {
                "messages": messages,
                "max_tokens": 4000,  # Increased for longer SOAP notes
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }
            
            # Try primary model first, fallback if decommissioned
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    **api_params
                )
            except Exception as primary_error:
                error_msg = str(primary_error).lower()
                if "decommissioned" in error_msg or "model" in error_msg:
                    logger.warning(f"Primary model {self.model} unavailable, trying fallback {self.fallback_model}")
                    try:
                        response = self.client.chat.completions.create(
                            model=self.fallback_model,
                            **api_params
                        )
                    except Exception as fallback_error:
                        logger.error(f"Both models failed: {fallback_error}")
                        raise Exception(f"SOAP generation failed: All models unavailable. Primary: {primary_error}, Fallback: {fallback_error}")
                else:
                    raise
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to parse JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # Fallback: Try to extract JSON from markdown code blocks
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                else:
                    # Last resort: Create basic structure from text
                    logger.warning("Failed to parse JSON, creating fallback structure")
                    result = {
                        "soap_note": content,
                        "subjective": "",
                        "objective": "",
                        "assessment": "",
                        "plan": "",
                        "entities": {
                            "symptoms": [],
                            "medications": [],
                            "diagnoses": [],
                            "vitals": {}
                        },
                        "icd_codes": []
                    }
            
            # Ensure all required fields exist
            soap_note = result.get("soap_note", "")
            entities = result.get("entities", {})
            icd_codes = result.get("icd_codes", [])
            
            # Extract structured sections if not provided
            if not result.get("subjective"):
                subjective_match = re.search(r'## Subjective\s*\n(.*?)(?=\n## |$)', soap_note, re.DOTALL)
                result["subjective"] = subjective_match.group(1).strip() if subjective_match else ""
            
            if not result.get("objective"):
                objective_match = re.search(r'## Objective\s*\n(.*?)(?=\n## |$)', soap_note, re.DOTALL)
                result["objective"] = objective_match.group(1).strip() if objective_match else ""
            
            if not result.get("assessment"):
                assessment_match = re.search(r'## Assessment\s*\n(.*?)(?=\n## |$)', soap_note, re.DOTALL)
                result["assessment"] = assessment_match.group(1).strip() if assessment_match else ""
            
            if not result.get("plan"):
                plan_match = re.search(r'## Plan\s*\n(.*?)(?=\n## |$)', soap_note, re.DOTALL)
                result["plan"] = plan_match.group(1).strip() if plan_match else ""
            
            logger.info(f"SOAP note generated: {len(soap_note)} characters")
            
            return {
                "soap_note": soap_note,
                "subjective": result.get("subjective", ""),
                "objective": result.get("objective", ""),
                "assessment": result.get("assessment", ""),
                "plan": result.get("plan", ""),
                "entities": entities,
                "icd_codes": icd_codes,
                "confidence": 0.9,  # LLM confidence estimate
                "model": self.model
            }
            
        except Exception as e:
            logger.error(f"SOAP generation failed: {str(e)}", exc_info=True)
            raise Exception(f"SOAP generation failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Professional medical scribe system prompt based on industry standards"""
        return """You are an expert medical scribe AI assistant specializing in converting doctor-patient consultations into professional, structured SOAP (Subjective, Objective, Assessment, Plan) notes.

Your expertise:
- Professional medical documentation following clinical standards
- Indian medical practice documentation conventions
- Accurate extraction of clinical information from conversations
- Structured organization of medical data
- Medical terminology and clinical accuracy

Documentation standards:
- Be thorough but concise
- Use standard medical terminology
- Include all relevant clinical findings
- Document medications with proper dosages, frequencies, and durations
- Include clear follow-up instructions
- Maintain professional medical language
- Follow SOAP note best practices

Always output valid JSON format with structured SOAP note and extracted entities.

CRITICAL: All SOAP note content must be in English only. Translate all Tamil/Telugu terms to English. Do NOT include Tamil/Telugu text or terms in brackets."""
    
    def _create_professional_prompt(self, transcript: str, language: str, lang_name: str, context: str) -> str:
        """Create professional medical scribe prompt with examples and detailed instructions"""
        
        examples = self._get_professional_examples(lang_name)
        
        prompt = f"""Convert this {lang_name} doctor-patient consultation transcript into a professional, structured SOAP medical note in English only.

Translate all medical terms, symptoms, and medications from {lang_name} to English. Do NOT include {lang_name} text or terms in brackets.

{examples}

**Current Consultation:**

{context}

**Instructions:**

1. **Subjective:** Patient complaints with duration. Output ONLY in English.
2. **Objective:** Vital signs (BP, pulse, temp), examination findings, observations. Output ONLY in English.
3. **Assessment:** Primary diagnosis using standard medical terminology. Output ONLY in English.
4. **Plan:** Medications with dosage, frequency (TID/BD/OD/SOS), duration. Output ONLY in English. Add follow-up instructions.

IMPORTANT: All output must be in English only. Do NOT include Tamil/Telugu terms or translations in brackets. Translate all medical terms to English.

Keep each section concise but complete. Use bullet points in markdown format.

**Output Format (JSON):**
{{
  "soap_note": "## Subjective\\n- Chief complaint with duration (English only)\\n\\n## Objective\\n- Vital signs and examination findings (English only)\\n\\n## Assessment\\n- Primary diagnosis (English only)\\n\\n## Plan\\n- Medication name with dosage, frequency, duration (English only)\\n- Follow-up instructions",
  "subjective": "Extracted subjective information in English",
  "objective": "All objective findings including vitals and examination in English",
  "assessment": "Clinical assessment/diagnosis in English",
  "plan": "Complete treatment plan with medications and follow-up in English",
  "entities": {{
    "symptoms": ["symptom1", "symptom2"],
    "medications": ["medication1 dosage frequency", "medication2 dosage frequency"],
    "diagnoses": ["diagnosis1", "diagnosis2"],
    "vitals": {{"bp": "120/80", "pulse": "72", "temp": "98.6"}}
  }},
  "icd_codes": ["A00.0", "B00.0"]
}}

CRITICAL: All text in soap_note, subjective, objective, assessment, and plan must be in English only. No Tamil/Telugu text or brackets.

Output ONLY valid JSON, no additional text."""
        
        return prompt
    
    def _get_professional_examples(self, lang_name: str) -> str:
        """Professional medical scribe examples - English only"""
        return """**Example:**

Transcript: "Patient has fever and cough for 3 days. BP 130/85. Prescribe Paracetamol 650mg three times daily."

Output JSON:
{
  "soap_note": "## Subjective\\n- Fever for 3 days\\n- Cough for 3 days\\n\\n## Objective\\n- Blood Pressure: 130/85 mmHg\\n\\n## Assessment\\n- Acute pharyngitis\\n\\n## Plan\\n- Paracetamol 650mg - Three times daily (TID) for 3 days\\n- Rest and adequate fluid intake\\n- Follow-up in 3 days if symptoms persist",
  "subjective": "Fever and cough for 3 days",
  "objective": "BP 130/85 mmHg",
  "assessment": "Acute pharyngitis",
  "plan": "Paracetamol 650mg TID for 3 days, rest, fluids, follow-up in 3 days",
  "entities": {"symptoms": ["Fever", "Cough"], "medications": ["Paracetamol 650mg"], "diagnoses": ["Acute pharyngitis"], "vitals": {"bp": "130/85"}},
  "icd_codes": ["J02.0"]
}"""
    
    def estimate_cost(self, transcript_length: int) -> float:
        """
        Estimate SOAP generation cost
        
        Args:
            transcript_length: Length of transcript in characters
        
        Returns:
            Estimated cost in ₹ (Groq is very cheap, ~₹0.01 per request)
        """
        # Groq pricing: ~₹0.01 per request for small models
        return 0.01

# Global service instance
soap_service = SOAPGenerationService()

