"""
Improved SOAP Generation Service
Enhanced prompt based on professional medical scribe documentation standards
"""

import groq
from app.config import settings
import logging
from typing import Dict, Any, Optional
import json
import re

logger = logging.getLogger(__name__)

class ImprovedSOAPGenerationService:
    """Enhanced SOAP Generation Service with professional medical documentation standards"""
    
    def __init__(self):
        """Initialize Groq client"""
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.1-70b-versatile"  # Use more capable model for better quality
    
    async def generate_soap_note(
        self,
        transcript: str,
        language: str,
        patient_name: Optional[str] = None,
        doctor_text: Optional[str] = None,
        patient_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate professional SOAP note following medical documentation standards
        
        Based on:
        - Professional medical scribe documentation practices
        - Indian clinic consultation note formats
        - Clinical documentation best practices
        """
        try:
            # Build enhanced prompt
            context = ""
            if doctor_text and patient_text:
                context = f"""
**Doctor's Speech:**
{doctor_text}

**Patient's Speech:**
{patient_text}
"""
            
            lang_name = "Tamil" if language == "ta" else "Telugu"
            
            # Professional medical scribe prompt
            prompt = self._create_professional_prompt(transcript, language, lang_name, context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2500,
                temperature=0.2,  # Lower temperature for more consistent, professional output
                top_p=0.9
            )
            
            content = response.choices[0].message.content
            
            # Parse response
            result = self._parse_response(content, transcript, language)
            
            return result
            
        except Exception as e:
            logger.error(f"SOAP generation failed: {e}", exc_info=True)
            return {
                "soap_note": self._create_fallback_note(transcript),
                "subjective": "",
                "objective": "",
                "assessment": "",
                "plan": "",
                "entities": {},
                "success": False,
                "error": str(e)
            }
    
    def _get_system_prompt(self) -> str:
        """Professional medical scribe system prompt"""
        return """You are an expert medical scribe AI assistant specializing in converting doctor-patient consultations into professional, structured SOAP (Subjective, Objective, Assessment, Plan) notes.

Your role:
- Accurately document clinical encounters following medical documentation standards
- Extract all relevant medical information from conversations
- Organize information into clear, professional SOAP format
- Maintain medical accuracy and clinical terminology
- Follow Indian medical practice documentation conventions
- Use concise, professional medical language

Documentation standards:
- Be thorough but concise
- Use standard medical terminology
- Include all relevant clinical findings
- Document medications with proper dosages and frequencies
- Include follow-up instructions clearly
- Maintain patient privacy and confidentiality

Output format:
- Always use clean Markdown formatting
- Use bullet points for lists
- Organize sections clearly
- Include Tamil/Telugu terms in brackets where relevant for clarity"""
    
    def _create_professional_prompt(self, transcript: str, language: str, lang_name: str, context: str) -> str:
        """Create professional medical scribe prompt with examples"""
        
        examples = self._get_professional_examples(lang_name)
        
        prompt = f"""Convert this {lang_name} doctor-patient consultation into a professional, structured SOAP medical note following medical documentation best practices.

{examples}

**Current Consultation:**

{context if context else f"**Full Transcript:**\n{transcript}"}

**Instructions for SOAP Note Generation:**

1. **Subjective (S) - Patient's History & Complaints:**
   - Document chief complaint(s) clearly
   - Include duration of symptoms
   - Note any relevant history (if mentioned)
   - Include Tamil/Telugu terms in brackets [term] after English translations
   - Format: Use bullet points, be specific and concise

2. **Objective (O) - Clinical Findings:**
   - Document vital signs (BP, pulse, temperature, etc.) if mentioned
   - Include physical examination findings
   - Note any observations made during consultation
   - Include lab values or test results if mentioned
   - Format: Use bullet points, include measurements with units

3. **Assessment (A) - Clinical Diagnosis:**
   - Provide primary diagnosis/diagnoses
   - Use standard medical terminology
   - Include ICD-10 compatible diagnosis names
   - If differential diagnosis mentioned, note it
   - Format: Use bullet points, be specific

4. **Plan (P) - Treatment Plan:**
   - List all medications with:
     * Generic name (brand name if mentioned)
     * Dosage (e.g., 500mg, 650mg)
     * Frequency (e.g., TID, BD, OD)
     * Duration (e.g., for 5 days, for 1 week)
   - Include Tamil/Telugu medication names in brackets
   - Note any lifestyle modifications or advice
   - Specify follow-up instructions (when, why)
   - Include any referrals or investigations ordered
   - Format: Use bullet points, be specific about dosages and schedules

**Formatting Requirements:**
- Use Markdown format with ## headers for sections
- Use bullet points (-) for all lists
- Keep each section concise but complete
- Maintain professional medical language
- Ensure all information from the conversation is captured

**Output the complete SOAP note in Markdown format:**"""
        
        return prompt
    
    def _get_professional_examples(self, lang_name: str) -> str:
        """Professional medical scribe examples"""
        if lang_name == "Tamil":
            return """
**Example 1 - Acute Illness:**

**Transcript:** "நோயாளிக்கு மூன்று நாட்களாக காய்ச்சல் மற்றும் இருமல் உள்ளது. BP 130/85, Pulse 92/min, Temperature 38.5°C. Throat examination shows mild redness. பாராசிட்டமால் 650mg மூன்று முறை, Amoxicillin 500mg இரண்டு முறை கொடுக்கவும். 3 நாட்களுக்குப் பிறகு follow-up."

**Output:**
## Subjective
- Fever [காய்ச்சல்] for 3 days
- Cough [இருமல்] for 3 days

## Objective
- Blood Pressure: 130/85 mmHg
- Pulse: 92/min
- Temperature: 38.5°C
- Throat examination: Mild redness noted

## Assessment
- Acute pharyngitis
- Fever, likely viral origin

## Plan
- Paracetamol [பாராசிட்டமால்] 650mg - Three times daily (TID) for 3 days
- Amoxicillin 500mg - Twice daily (BD) for 5 days
- Rest and adequate fluid intake
- Follow-up in 3 days if symptoms persist or worsen

---

**Example 2 - Chronic Condition:**

**Transcript:** "தலைவலி இரண்டு வாரங்களாக தொடர்ந்து வருகிறது. Eye examination normal. BP 140/90. Tension headache என்று நினைக்கிறேன். Rest advised, Paracetamol 500mg SOS."

**Output:**
## Subjective
- Headache [தலைவலி] for 2 weeks, continuous

## Objective
- Blood Pressure: 140/90 mmHg
- Eye examination: Normal
- General appearance: No acute distress

## Assessment
- Tension headache
- Hypertension (BP elevated)

## Plan
- Paracetamol 500mg - As needed (SOS) for pain relief
- Rest and stress management
- Monitor blood pressure
- Follow-up in 1 week or if symptoms worsen
- Consider lifestyle modifications for BP control"""
        else:  # Telugu
            return """
**Example 1 - Acute Illness:**

**Transcript:** "రోగికి మూడు రోజుల నుండి జ్వరం మరియు దగ్గు ఉంది. BP 130/85, Pulse 92/min. Throat examination shows mild redness. Paracetamol 650mg మూడు సార్లు, Amoxicillin 500mg రెండు సార్లు ఇవ్వండి."

**Output:**
## Subjective
- Fever [జ్వరం] for 3 days
- Cough [దగ్గు] for 3 days

## Objective
- Blood Pressure: 130/85 mmHg
- Pulse: 92/min
- Throat examination: Mild redness noted

## Assessment
- Acute pharyngitis

## Plan
- Paracetamol 650mg - Three times daily (TID) for 3 days
- Amoxicillin 500mg - Twice daily (BD) for 5 days
- Rest and adequate fluid intake
- Follow-up in 3 days if symptoms persist"""
    
    def _parse_response(self, content: str, transcript: str, language: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            # Try to extract JSON if present
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
                return {
                    "soap_note": result.get("soap_note", content),
                    "subjective": result.get("subjective", ""),
                    "objective": result.get("objective", ""),
                    "assessment": result.get("assessment", ""),
                    "plan": result.get("plan", ""),
                    "entities": result.get("entities", {}),
                    "success": True
                }
        except:
            pass
        
        # Extract sections from markdown
        sections = self._extract_sections_from_markdown(content)
        
        return {
            "soap_note": content,
            "subjective": sections.get("subjective", ""),
            "objective": sections.get("objective", ""),
            "assessment": sections.get("assessment", ""),
            "plan": sections.get("plan", ""),
            "entities": {},
            "success": True
        }
    
    def _extract_sections_from_markdown(self, markdown: str) -> Dict[str, str]:
        """Extract SOAP sections from markdown text"""
        sections = {
            "subjective": "",
            "objective": "",
            "assessment": "",
            "plan": ""
        }
        
        # Pattern to match sections
        patterns = {
            "subjective": r"##\s*Subjective.*?\n(.*?)(?=##|$)",
            "objective": r"##\s*Objective.*?\n(.*?)(?=##|$)",
            "assessment": r"##\s*Assessment.*?\n(.*?)(?=##|$)",
            "plan": r"##\s*Plan.*?\n(.*?)(?=##|$)"
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, markdown, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section] = match.group(1).strip()
        
        return sections
    
    def _create_fallback_note(self, transcript: str) -> str:
        """Create fallback SOAP note"""
        return f"""# Medical Consultation Note

**Note:** AI generation unavailable. Please review and edit manually.

## Subjective
- [To be filled from transcript]

## Objective
- [To be filled from transcript]

## Assessment
- [To be filled from transcript]

## Plan
- [To be filled from transcript]

**Original Transcript:**
{transcript[:500]}..."""

