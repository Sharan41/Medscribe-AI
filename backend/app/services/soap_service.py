"""
SOAP Generation Service - Phase 1 Enhanced
Generates structured SOAP notes from transcripts using Google Gemini
Enhanced with Indian clinical examples and improved prompt engineering
"""

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.config import settings
import logging
from typing import Dict, Any, Optional, List
import json
import re
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Optional: Hugging Face NER for entity validation (Phase 1)
# Uncomment when ready to integrate
# try:
#     from transformers import pipeline
#     NER_AVAILABLE = True
# except ImportError:
#     NER_AVAILABLE = False
#     logger.info("Hugging Face transformers not available. NER validation disabled.")
NER_AVAILABLE = False  # Set to True when ready to integrate

class SOAPGenerationService:
    """Service for generating SOAP notes using Google Gemini - Phase 1 Enhanced"""
    
    def __init__(self):
        """Initialize Gemini client and load Indian clinical examples"""
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
        
        # Load Indian clinical examples for few-shot learning
        self.examples = self._load_indian_examples()
        
        # Initialize NER models if available (Phase 1 - optional)
        self.medical_ner = None
        if NER_AVAILABLE:
            try:
                self.medical_ner = pipeline(
                    "ner",
                    model="AventIQ-AI/bert-medical-entity-extraction",
                    aggregation_strategy="simple"
                )
                logger.info("Medical NER model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load NER model: {e}")
                self.medical_ner = None
    
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
                # Try multiple patterns to extract Assessment
                assessment_match = re.search(r'## Assessment\s*\n(.*?)(?=\n## |$)', soap_note, re.DOTALL)
                if not assessment_match:
                    assessment_match = re.search(r'Assessment[:\-]?\s*\n(.*?)(?=\nPlan|$)', soap_note, re.DOTALL | re.IGNORECASE)
                result["assessment"] = assessment_match.group(1).strip() if assessment_match else "Clinical assessment pending further evaluation"
            
            if not result.get("plan"):
                # Try multiple patterns to extract Plan
                plan_match = re.search(r'## Plan\s*\n(.*?)(?=\n## |$)', soap_note, re.DOTALL)
                if not plan_match:
                    plan_match = re.search(r'Plan[:\-]?\s*\n(.*?)$', soap_note, re.DOTALL | re.IGNORECASE)
                result["plan"] = plan_match.group(1).strip() if plan_match else "Symptomatic management and follow-up recommended"
            
            logger.info(f"SOAP note generated: {len(soap_note)} characters")
            
            # Ensure Assessment and Plan are never empty
            assessment = result.get("assessment", "").strip()
            plan = result.get("plan", "").strip()
            
            # Log if Assessment or Plan are missing for debugging
            if not assessment:
                logger.warning("Assessment section missing from LLM response, using fallback")
                assessment = "Clinical assessment pending further evaluation"
            if not plan:
                logger.warning("Plan section missing from LLM response, using fallback")
                plan = "Symptomatic management and follow-up recommended"
            
            logger.info(f"SOAP sections - Subjective: {bool(result.get('subjective'))}, Objective: {bool(result.get('objective'))}, Assessment: {bool(assessment)}, Plan: {bool(plan)}")
            
            return {
                "soap_note": soap_note,
                "subjective": result.get("subjective", ""),
                "objective": result.get("objective", ""),
                "assessment": assessment,
                "plan": plan,
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
    
    def _classify_condition_type(self, transcript: str) -> Optional[str]:
        """Classify condition type from transcript for better example selection"""
        transcript_lower = transcript.lower()
        
        if any(term in transcript_lower for term in ["fever", "cough", "cold", "respiratory", "throat", "nasal"]):
            return "respiratory"
        elif any(term in transcript_lower for term in ["abdominal", "stomach", "gastritis", "vomiting", "diarrhea"]):
            return "gastrointestinal"
        elif any(term in transcript_lower for term in ["chest pain", "hypertension", "heart", "bp", "blood pressure"]):
            return "cardiovascular"
        elif any(term in transcript_lower for term in ["headache", "dizziness", "seizure", "neurological"]):
            return "neurological"
        elif any(term in transcript_lower for term in ["diabetes", "sugar", "fbs", "diabetic"]):
            return "endocrine"
        else:
            return None
    
    def _create_professional_prompt(self, transcript: str, language: str, lang_name: str, context: str) -> str:
        """Create professional medical scribe prompt with Indian examples - Phase 1 Enhanced"""
        
        # Classify condition type for better example selection
        condition_type = self._classify_condition_type(transcript)
        examples = self._get_professional_examples(condition_type)
        
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
   - **CRITICAL:** You MUST provide an assessment/diagnosis. If no clear diagnosis, use: "Clinical assessment pending further evaluation" or "Symptomatic treatment indicated"
   - **DO NOT leave empty.** Always provide a clinical assessment.
4. **Plan:** Medications with dosage, frequency (TID/BD/OD/SOS), duration. Output ONLY in English. Add follow-up instructions.
   - **CRITICAL:** You MUST provide a treatment plan. If no medications mentioned, use: "Symptomatic management recommended" or "Supportive care advised"
   - **DO NOT leave empty.** Always provide a plan with at least follow-up instructions.

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

CRITICAL REQUIREMENTS:
1. All text in soap_note, subjective, objective, assessment, and plan must be in English only. No Tamil/Telugu text or brackets.
2. You MUST include all 4 sections: Subjective, Objective, Assessment, and Plan in the soap_note markdown.
3. You MUST provide values for assessment and plan fields in the JSON response.
4. If assessment is unclear, use: "Clinical assessment pending further evaluation" or "Symptomatic treatment indicated"
5. If plan is unclear, use: "Symptomatic management recommended" or "Supportive care and follow-up advised"
6. DO NOT leave assessment or plan empty. Always provide meaningful clinical content.

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
    
    def _load_indian_examples(self) -> List[Dict]:
        """Load Indian clinical examples from JSON file"""
        examples_file = Path(__file__).parent.parent.parent / "data" / "indian_clinical_examples.json"
        
        try:
            if examples_file.exists():
                with open(examples_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    examples = data.get("examples", [])
                    # Filter to validated examples only
                    validated = [ex for ex in examples if ex.get("validated", False)]
                    logger.info(f"Loaded {len(validated)} validated Indian clinical examples")
                    return validated
            else:
                logger.warning(f"Examples file not found: {examples_file}. Using default examples.")
                return []
        except Exception as e:
            logger.error(f"Failed to load Indian examples: {e}. Using default examples.")
            return []
    
    def _get_professional_examples(self, condition_type: Optional[str] = None) -> str:
        """Get professional medical scribe examples - Enhanced with Indian examples"""
        
        # Try to get Indian examples first
        if self.examples:
            # Select examples based on condition type if available
            selected_examples = []
            if condition_type:
                # Try to find examples matching condition type
                matching = [ex for ex in self.examples if ex.get("condition_type") == condition_type]
                if matching:
                    selected_examples = matching[:2]  # Use 2 matching examples
                else:
                    selected_examples = self.examples[:2]  # Fallback to first 2
            else:
                # Get diverse examples from different categories
                selected_examples = self.examples[:3]  # Use first 3 examples
            
            if selected_examples:
                examples_text = "**Indian Clinical Examples:**\n\n"
                for i, ex in enumerate(selected_examples, 1):
                    transcript = ex.get("transcript_english") or ex.get("transcript", "")
                    soap = ex.get("soap_note", {})
                    
                    examples_text += f"""**Example {i} ({ex.get('condition_type', 'general')}):**

Transcript: "{transcript}"

Output JSON:
{{
  "soap_note": "## Subjective\\n{soap.get('subjective', '').replace(chr(10), '\\n')}\\n\\n## Objective\\n{soap.get('objective', '').replace(chr(10), '\\n')}\\n\\n## Assessment\\n{soap.get('assessment', '')}\\n\\n## Plan\\n{soap.get('plan', '').replace(chr(10), '\\n')}",
  "subjective": "{soap.get('subjective', '')}",
  "objective": "{soap.get('objective', '')}",
  "assessment": "{soap.get('assessment', '')}",
  "plan": "{soap.get('plan', '')}",
  "entities": {json.dumps(ex.get('entities', {}))},
  "icd_codes": {json.dumps(ex.get('icd_codes', []))}
}}

"""
                return examples_text
        
        # Fallback to default example if no Indian examples available
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
    
    def _extract_entities_with_ner(self, transcript: str) -> Dict[str, Any]:
        """
        Extract medical entities using NER models (Phase 1 - optional)
        Returns entities for validation against LLM output
        """
        if not self.medical_ner:
            return {}
        
        try:
            # Extract entities using NER model
            entities = self.medical_ner(transcript)
            
            # Format entities
            formatted = {
                "symptoms": [],
                "medications": [],
                "diagnoses": [],
                "vitals": {}
            }
            
            for entity in entities:
                entity_type = entity.get("entity_group", "").upper()
                entity_text = entity.get("word", "")
                
                if "SYMPTOM" in entity_type or "DISEASE" in entity_type:
                    formatted["symptoms"].append(entity_text)
                elif "MEDICATION" in entity_type or "DRUG" in entity_type:
                    formatted["medications"].append(entity_text)
                elif "DIAGNOSIS" in entity_type:
                    formatted["diagnoses"].append(entity_text)
            
            return formatted
        except Exception as e:
            logger.warning(f"NER entity extraction failed: {e}")
            return {}
    
    def collect_feedback(self, consultation_id: str, original_soap: Dict[str, Any], 
                        edited_soap: Dict[str, Any]) -> bool:
        """
        Collect doctor feedback/edits for future training (Phase 1)
        Saves edits to feedback file for later use in fine-tuning
        
        Args:
            consultation_id: Consultation ID
            original_soap: Original SOAP note generated by AI
            edited_soap: Edited SOAP note by doctor
        
        Returns:
            True if feedback saved successfully
        """
        try:
            feedback_file = Path(__file__).parent.parent.parent / "data" / "doctor_feedback.json"
            
            # Load existing feedback
            feedback_data = []
            if feedback_file.exists():
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedback_data = json.load(f)
            
            # Create feedback entry
            from datetime import datetime
            feedback_entry = {
                "consultation_id": consultation_id,
                "timestamp": datetime.now().isoformat(),
                "original_soap": original_soap,
                "edited_soap": edited_soap,
                "changes": self._compute_soap_diff(original_soap, edited_soap)
            }
            
            feedback_data.append(feedback_entry)
            
            # Save feedback
            feedback_file.parent.mkdir(parents=True, exist_ok=True)
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Feedback collected for consultation {consultation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to collect feedback: {e}")
            return False
    
    def _compute_soap_diff(self, original: Dict[str, Any], edited: Dict[str, Any]) -> Dict[str, Any]:
        """Compute differences between original and edited SOAP notes"""
        diff = {}
        
        for section in ["subjective", "objective", "assessment", "plan"]:
            orig_text = original.get(section, "").strip()
            edit_text = edited.get(section, "").strip()
            
            if orig_text != edit_text:
                diff[section] = {
                    "original": orig_text,
                    "edited": edit_text,
                    "changed": True
                }
        
        return diff
    
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

