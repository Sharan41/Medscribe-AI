"""
LLM-Powered SOAP Note Generator
Uses Groq LLM to convert transcripts directly to SOAP notes
"""

import groq
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY")
client = groq.Groq(api_key=GROQ_API_KEY)

class TranscriptRequest(BaseModel):
    transcript: str
    language: str = "ta"  # "ta" for Tamil, "te" for Telugu
    patient_name: Optional[str] = "Patient"
    doctor_name: Optional[str] = "Dr. Name"

class SOAPGenerator:
    def __init__(self):
        self.client = client
    
    def generate_soap_note(self, request: TranscriptRequest) -> dict:
        """
        Generate SOAP note from transcript using LLM
        
        Args:
            request: TranscriptRequest with transcript and metadata
            
        Returns:
            dict with soap_note and metadata
        """
        # Create prompt
        prompt = self._create_prompt(request.transcript, request.language)
        
        try:
            # Call LLM
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",  # or "llama-3.2-1b-preview" for faster
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical assistant that converts doctor-patient conversations into structured SOAP notes. Always maintain medical accuracy and include Tamil/Telugu terms in brackets."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3  # Lower temperature for more consistent medical output
            )
            
            soap_note = response.choices[0].message.content
            
            return {
                "soap_note": soap_note,
                "patient_name": request.patient_name,
                "doctor_name": request.doctor_name,
                "date": datetime.now().isoformat(),
                "language": request.language,
                "success": True
            }
        
        except Exception as e:
            # Fallback to rule-based if LLM fails
            print(f"LLM generation failed: {e}, using fallback")
            return self._fallback_generation(request)
    
    def _create_prompt(self, transcript: str, language: str) -> str:
        """
        Create prompt for LLM with few-shot examples
        """
        lang_name = "Tamil" if language == "ta" else "Telugu"
        
        # Few-shot examples for better accuracy
        examples = """
**Example 1:**

Input Transcript: "நோயாளிக்கு காய்ச்சல் உள்ளது. BP 120/80. பாராசிட்டமால் கொடுக்கவும்."

Output:
## Subjective (Patient Complaints)
- Fever [காய்ச்சல்]

## Objective (Examination Findings)
- Blood Pressure: 120/80 mmHg

## Assessment (Diagnosis)
- Viral fever

## Plan (Treatment)
- Paracetamol 500mg [பாராசிட்டமால்] - Three times daily for 3 days
- Rest and adequate hydration

---

**Example 2:**

Input Transcript: "தலைவலி மற்றும் கண் பார்வை பிரச்சனை. Eye examination normal. Rest advised."

Output:
## Subjective (Patient Complaints)
- Headache [தலைவலி]
- Vision problems [கண் பார்வை பிரச்சனை]

## Objective (Examination Findings)
- Eye examination: Normal

## Assessment (Diagnosis)
- Tension headache

## Plan (Treatment)
- Rest and observation
- Follow-up if symptoms persist
"""
        
        prompt = f"""
Convert this {lang_name} doctor-patient conversation into a structured SOAP medical note.

{examples}

**Now convert this conversation:**

Transcript: {transcript}

**Instructions:**
1. Extract all medical information from the conversation
2. Organize into SOAP format:
   - **Subjective:** Patient complaints and symptoms (include {lang_name} terms in brackets)
   - **Objective:** Examination findings, vital signs, observations
   - **Assessment:** Diagnosis or clinical impression
   - **Plan:** Treatment plan, medications (with dosage), follow-up instructions

3. Maintain medical accuracy
4. Include original {lang_name} terms in brackets after English translations
5. Format as clean Markdown following the examples above

**Output the SOAP note now:**
"""
        return prompt
    
    def _fallback_generation(self, request: TranscriptRequest) -> dict:
        """
        Fallback rule-based generation if LLM fails
        """
        # Simple fallback - can be enhanced with rule-based logic
        return {
            "soap_note": f"# Medical Consultation Note\n\n**Note:** LLM generation unavailable. Please edit manually.\n\n**Transcript:**\n{request.transcript}",
            "patient_name": request.patient_name,
            "doctor_name": request.doctor_name,
            "date": datetime.now().isoformat(),
            "language": request.language,
            "success": False,
            "fallback": True
        }

# Usage example
if __name__ == "__main__":
    generator = SOAPGenerator()
    
    request = TranscriptRequest(
        transcript="நோயாளிக்கு காய்ச்சல் மற்றும் தலைவலி உள்ளது. BP 120/80. பாராசிட்டமால் 500mg மூன்று முறை கொடுக்கவும்.",
        language="ta",
        patient_name="Patient Name",
        doctor_name="Dr. Priya"
    )
    
    result = generator.generate_soap_note(request)
    print(result["soap_note"])

