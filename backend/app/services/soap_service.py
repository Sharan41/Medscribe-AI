"""
SOAP Generation Service
Generates structured SOAP notes from transcripts using Google Gemini
"""

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.config import settings
import logging
from typing import Dict, Any, Optional
import json
import re
import os

logger = logging.getLogger(__name__)

class SOAPGenerationService:
    """Service for generating SOAP notes using Google Gemini"""
    
    def __init__(self):
        """Initialize Gemini client"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Use Gemini 2.0 Flash for medical documentation (best balance of speed and quality)
        # Alternative: models/gemini-2.5-flash for latest version
        self.model = genai.GenerativeModel(
            model_name="models/gemini-2.0-flash",
            generation_config={
                "temperature": 0.1,  # Medical precision
                "top_p": 0.8,
                "max_output_tokens": 4000,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
    
    async def generate_soap_note(
        self,
        transcript: str,
        language: str,
        patient_name: Optional[str] = None,
        doctor_text: Optional[str] = None,
        patient_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured SOAP note from transcript using Gemini
        
        Args:
            transcript: Full transcript text
            language: Language code ("ta" for Tamil, "te" for Telugu)
            patient_name: Patient name (optional)
            doctor_text: Doctor's speech only (if diarization available)
            patient_text: Patient's speech only (if diarization available)
        
        Returns:
            Dictionary with SOAP note and extracted entities
        """
        try:
            # Build context
            if doctor_text and patient_text:
                context = f"""**Doctor's Speech:**
{doctor_text}

**Patient's Speech:**
{patient_text}
"""
            else:
                context = f"**Full Transcript:**\n{transcript}"
            
            lang_name = "Tamil" if language == "ta" else "Telugu"
            
            # Create professional medical scribe prompt
            prompt = self._create_professional_prompt(transcript, language, lang_name, context)
            
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Parse response
            content = response.text
            
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
                "success": True
            }
            
        except Exception as e:
            logger.error(f"SOAP generation failed: {e}", exc_info=True)
            raise Exception(f"SOAP generation failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Professional medical scribe system prompt"""
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
- Auto-generate ICD-10 codes for diagnoses

CRITICAL: All SOAP note content must be in English only. Translate all Tamil/Telugu terms to English. Do NOT include Tamil/Telugu text or terms in brackets."""
    
    def _create_professional_prompt(self, transcript: str, language: str, lang_name: str, context: str) -> str:
        """Create professional medical scribe prompt with examples"""
        
        examples = self._get_professional_examples()
        
        # Extract symptoms from transcript for inference (simple keyword matching)
        symptom_keywords = ['fever', 'cough', 'pain', 'headache', 'abdominal', 'chest', 'breathing', 
                           'throat', 'stomach', 'nausea', 'vomiting', 'diarrhea', 'dizziness', 
                           'weakness', 'joint', 'muscle', 'back']
        detected_symptoms = [kw for kw in symptom_keywords if kw.lower() in transcript.lower()]
        exam_template = self._get_physical_exam_template(detected_symptoms) if detected_symptoms else ""
        
        prompt = f"""Convert this {lang_name} doctor-patient consultation transcript into a professional, structured SOAP medical note in English only.

Translate all medical terms, symptoms, and medications from {lang_name} to English. Do NOT include {lang_name} text or terms in brackets.

{examples}

**Current Consultation:**

{context}

**Instructions:**

1. **Subjective:** Patient complaints with duration. Output ONLY in English.
2. **Objective:** Extract ALL objective findings from the transcript:
   - **Vital Signs:** Extract BP, pulse, temperature, respiratory rate, SpO2, weight, height if mentioned
   - **Physical Examination:** Document all examination findings mentioned:
     * General appearance (if mentioned: alert, distressed, comfortable, etc.)
     * Cardiovascular: Heart sounds, murmurs, peripheral pulses, edema
     * Respiratory: Breath sounds, chest examination findings
     * Abdominal: Tenderness, distension, bowel sounds, organomegaly
     * Neurological: Mental status, reflexes, motor/sensory findings
     * Other systems: Any examination findings mentioned
   - **Laboratory/Diagnostic Tests:** Document any lab values, imaging results, or test findings mentioned
   - **Inference Rules:** If transcript mentions symptoms but no examination, infer common examinations:
     * Fever/cough → Document: "General appearance: Alert. Respiratory examination: [infer based on symptoms]"
     * Abdominal pain → Document: "Abdominal examination: [infer based on symptoms]"
     * Headache → Document: "Neurological examination: [infer basic findings]"
   - **Structured Physical Exam Template:** Use this as guidance for common examinations:
{exam_template if exam_template else "     * General appearance, vital signs, and system-specific examinations based on symptoms"}
   - **If NO objective findings mentioned:** Write: "Objective findings: Not documented in consultation. Clinical examination recommended."
   - **DO NOT leave empty.** Always provide meaningful objective documentation.
   - Output ONLY in English.
3. **Assessment:** Primary diagnosis using standard medical terminology. Auto-generate ICD-10 codes. Output ONLY in English.
4. **Plan:** Medications with dosage, frequency (TID/BD/OD/SOS), duration. Output ONLY in English. Add follow-up instructions.

IMPORTANT: All output must be in English only. Do NOT include Tamil/Telugu terms or translations in brackets. Translate all medical terms to English.

Keep each section concise but complete. Use bullet points in markdown format.

**Output Format (JSON):**
{{
  "soap_note": "## Subjective\\n- Chief complaint with duration (English only)\\n\\n## Objective\\n- Vital signs and examination findings (English only)\\n\\n## Assessment\\n- Primary diagnosis (English only)\\n\\n## Plan\\n- Medication name with dosage, frequency, duration (English only)\\n- Follow-up instructions",
  "subjective": "Extracted subjective information in English",
  "objective": "All objective findings including vitals, physical examination, and diagnostic tests in English. Use inference for common examinations based on symptoms. If none mentioned, state 'Objective findings: Not documented in consultation. Clinical examination recommended.'",
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
    
    def _get_physical_exam_template(self, symptoms: list) -> str:
        """
        Generate structured physical examination template based on symptoms
        Helps infer common examinations that should be documented
        """
        template_sections = []
        
        # Always include general appearance
        template_sections.append("- General Appearance: Alert, comfortable (if not mentioned, infer from context)")
        
        # Infer examinations based on symptoms
        symptoms_lower = [s.lower() for s in symptoms]
        
        if any(s in symptoms_lower for s in ['fever', 'cough', 'breathing', 'chest', 'throat', 'cold']):
            template_sections.append("- Respiratory Examination: Assess breath sounds, respiratory rate, chest expansion")
            template_sections.append("- Throat Examination: Inspect for erythema, exudate, or other findings")
        
        if any(s in symptoms_lower for s in ['abdominal', 'stomach', 'pain', 'nausea', 'vomiting', 'diarrhea']):
            template_sections.append("- Abdominal Examination: Inspect, auscultate, palpate, percuss abdomen")
            template_sections.append("- Assess for tenderness, distension, organomegaly, bowel sounds")
        
        if any(s in symptoms_lower for s in ['headache', 'dizziness', 'seizure', 'weakness', 'numbness']):
            template_sections.append("- Neurological Examination: Mental status, cranial nerves, motor/sensory function")
            template_sections.append("- Assess reflexes, coordination, gait if relevant")
        
        if any(s in symptoms_lower for s in ['chest pain', 'heart', 'palpitation', 'shortness']):
            template_sections.append("- Cardiovascular Examination: Heart sounds, rhythm, peripheral pulses")
            template_sections.append("- Assess for murmurs, gallops, or other abnormal findings")
        
        if any(s in symptoms_lower for s in ['joint', 'muscle', 'back', 'limb']):
            template_sections.append("- Musculoskeletal Examination: Inspect affected area, assess range of motion")
            template_sections.append("- Palpate for tenderness, swelling, or deformity")
        
        return "\n".join(template_sections)
    
    def _get_professional_examples(self) -> str:
        """Professional medical scribe examples - English only"""
        return """**Example:**

Transcript: "Patient has fever and cough for 3 days. BP 130/85. Prescribe Paracetamol 650mg three times daily."

Output JSON:
{
  "soap_note": "## Subjective\\n- Fever for 3 days\\n- Cough for 3 days\\n\\n## Objective\\n- Vital Signs: Blood Pressure 130/85 mmHg, Pulse regular\\n- General Appearance: Alert, comfortable\\n- Respiratory Examination: Mild tachypnea noted, no obvious respiratory distress\\n- Throat Examination: Mild erythema noted (inferred from symptoms)\\n\\n## Assessment\\n- Acute pharyngitis\\n\\n## Plan\\n- Paracetamol 650mg - Three times daily (TID) for 3 days\\n- Rest and adequate fluid intake\\n- Follow-up in 3 days if symptoms persist",
  "subjective": "Fever and cough for 3 days",
  "objective": "Vital Signs: BP 130/85 mmHg. General: Alert. Respiratory: Mild tachypnea. Throat: Mild erythema (inferred).",
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
            Estimated cost in ₹ (Gemini: ~₹0.15 per note)
        """
        # Gemini pricing: ~₹0.15 per note for gemini-2.0-flash-exp
        return 0.15

# Global service instance
soap_service = SOAPGenerationService()

