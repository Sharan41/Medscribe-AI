"""
Test if Gemini model has learned from the Indian clinical examples
Compares SOAP generation with and without examples
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

import google.generativeai as genai
import os

# Get API key from environment or .env
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    # Try loading from .env file
    env_file = Path(backend_dir) / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    gemini_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

if not gemini_key:
    raise ValueError("GEMINI_API_KEY not found. Set it in environment or backend/.env")

genai.configure(api_key=gemini_key)

# Import the SOAP service (handle import errors gracefully)
try:
    from app.services.soap_service import SOAPGenerationService
    SOAP_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import SOAP service: {e}")
    print("Will use direct Gemini calls instead")
    SOAP_SERVICE_AVAILABLE = False
    SOAPGenerationService = None

class ExampleLearningTester:
    def __init__(self):
        """Initialize tester"""
        self.model = genai.GenerativeModel("models/gemini-2.0-flash")
        
        if SOAP_SERVICE_AVAILABLE:
            self.soap_service = SOAPGenerationService()
        else:
            self.soap_service = None
            print("⚠️  Using direct Gemini calls (SOAP service not available)")
        
        # Load examples
        examples_file = Path(backend_dir) / "data" / "indian_clinical_examples.json"
        with open(examples_file, 'r') as f:
            self.examples_data = json.load(f)
        
        self.examples = [ex for ex in self.examples_data['examples'] if ex.get('validated', False)]
        print(f"✅ Loaded {len(self.examples)} validated examples")
    
    def test_with_examples(self, transcript: str, language: str = "en") -> Dict:
        """Test SOAP generation WITH examples (current system)"""
        if self.soap_service:
            import asyncio
            try:
                return asyncio.run(self.soap_service.generate_soap_note(
                    transcript=transcript,
                    language=language
                ))
            except:
                # Fallback to direct call
                pass
        
        # Direct call with examples
        return self._generate_with_examples_direct(transcript, language)
    
    def _generate_with_examples_direct(self, transcript: str, language: str) -> Dict:
        """Generate SOAP with examples using direct Gemini call"""
        # Get examples
        examples_text = ""
        if self.examples:
            selected = self.examples[:3]  # Use first 3
            examples_text = "**Indian Clinical Examples:**\n\n"
            for i, ex in enumerate(selected, 1):
                soap = ex.get("soap_note", {})
                examples_text += f"Example {i}:\n"
                examples_text += f"Transcript: {ex.get('transcript', '')[:100]}...\n"
                examples_text += f"SOAP: Assessment: {soap.get('assessment', '')}\n"
                examples_text += f"Plan: {soap.get('plan', '')[:100]}...\n\n"
        
        prompt = f"""Convert this medical consultation transcript into a structured SOAP note following Indian medical documentation standards.

{examples_text}

Current Transcript: {transcript}

Generate a complete SOAP note with:
- Subjective: Patient complaints with duration
- Objective: Vital signs, physical examination findings
- Assessment: Primary diagnosis using standard medical terminology with ICD-10 code
- Plan: Medications with dosage, frequency (TID/BD/OD/SOS), duration, and follow-up instructions

Output as JSON:
{{
  "subjective": "...",
  "objective": "...",
  "assessment": "...",
  "plan": "...",
  "entities": {{
    "symptoms": [...],
    "medications": [...],
    "diagnoses": [...],
    "vitals": {{}}
  }},
  "icd_codes": [...]
}}"""
        
        response = self.model.generate_content(prompt)
        content = response.text.strip()
        
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                result = {"error": "Could not parse JSON"}
        
        return {
            "soap_note": content,
            "subjective": result.get("subjective", ""),
            "objective": result.get("objective", ""),
            "assessment": result.get("assessment", ""),
            "plan": result.get("plan", ""),
            "entities": result.get("entities", {}),
            "icd_codes": result.get("icd_codes", [])
        }
    
    def test_without_examples(self, transcript: str, language: str = "en") -> Dict:
        """Test SOAP generation WITHOUT examples (baseline)"""
        # Create a temporary service without examples
        lang_name = "Tamil" if language == "ta" else "Telugu"
        
        prompt = f"""Convert this {lang_name} doctor-patient consultation transcript into a structured SOAP medical note in English only.

Transcript: {transcript}

Generate a complete SOAP note with:
- Subjective: Patient complaints with duration
- Objective: Vital signs, physical examination findings
- Assessment: Primary diagnosis using standard medical terminology with ICD-10 code
- Plan: Medications with dosage, frequency (TID/BD/OD/SOS), duration, and follow-up instructions

Output as JSON:
{{
  "subjective": "...",
  "objective": "...",
  "assessment": "...",
  "plan": "...",
  "entities": {{
    "symptoms": [...],
    "medications": [...],
    "diagnoses": [...],
    "vitals": {{}}
  }},
  "icd_codes": [...]
}}

All output must be in English. Use standard medical terminology."""
        
        response = self.model.generate_content(prompt)
        content = response.text.strip()
        
        # Parse JSON
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                result = {"error": "Could not parse JSON"}
        
        return {
            "soap_note": content,
            "subjective": result.get("subjective", ""),
            "objective": result.get("objective", ""),
            "assessment": result.get("assessment", ""),
            "plan": result.get("plan", ""),
            "entities": result.get("entities", {}),
            "icd_codes": result.get("icd_codes", [])
        }
    
    def compare_outputs(self, transcript: str, language: str = "en"):
        """Compare outputs with and without examples"""
        print("\n" + "="*60)
        print("TESTING: Example Learning Verification")
        print("="*60)
        print(f"\n📝 Test Transcript:")
        print(f"   {transcript[:200]}...")
        
        print("\n🔄 Generating SOAP WITH examples (current system)...")
        with_examples = self.test_with_examples(transcript, language)
        
        print("🔄 Generating SOAP WITHOUT examples (baseline)...")
        without_examples = self.test_without_examples(transcript, language)
        
        print("\n" + "="*60)
        print("COMPARISON RESULTS")
        print("="*60)
        
        # Compare key metrics
        metrics = {
            "with_examples": {
                "has_assessment": bool(with_examples.get("assessment", "")),
                "has_plan": bool(with_examples.get("plan", "")),
                "has_icd_codes": len(with_examples.get("icd_codes", [])) > 0,
                "objective_length": len(with_examples.get("objective", "")),
                "plan_length": len(with_examples.get("plan", "")),
                "medications_count": len(with_examples.get("entities", {}).get("medications", []))
            },
            "without_examples": {
                "has_assessment": bool(without_examples.get("assessment", "")),
                "has_plan": bool(without_examples.get("plan", "")),
                "has_icd_codes": len(without_examples.get("icd_codes", [])) > 0,
                "objective_length": len(without_examples.get("objective", "")),
                "plan_length": len(without_examples.get("plan", "")),
                "medications_count": len(without_examples.get("entities", {}).get("medications", []))
            }
        }
        
        print("\n📊 Metrics Comparison:")
        print(f"   Assessment present:")
        print(f"      With examples: {metrics['with_examples']['has_assessment']} ✅" if metrics['with_examples']['has_assessment'] else "      With examples: ❌")
        print(f"      Without examples: {metrics['without_examples']['has_assessment']} ✅" if metrics['without_examples']['has_assessment'] else "      Without examples: ❌")
        
        print(f"\n   Plan present:")
        print(f"      With examples: {metrics['with_examples']['has_plan']} ✅" if metrics['with_examples']['has_plan'] else "      With examples: ❌")
        print(f"      Without examples: {metrics['without_examples']['has_plan']} ✅" if metrics['without_examples']['has_plan'] else "      Without examples: ❌")
        
        print(f"\n   ICD codes:")
        print(f"      With examples: {metrics['with_examples']['has_icd_codes']} ({len(with_examples.get('icd_codes', []))} codes)")
        print(f"      Without examples: {metrics['without_examples']['has_icd_codes']} ({len(without_examples.get('icd_codes', []))} codes)")
        
        print(f"\n   Objective section length:")
        print(f"      With examples: {metrics['with_examples']['objective_length']} chars")
        print(f"      Without examples: {metrics['without_examples']['objective_length']} chars")
        
        print(f"\n   Plan section length:")
        print(f"      With examples: {metrics['with_examples']['plan_length']} chars")
        print(f"      Without examples: {metrics['without_examples']['plan_length']} chars")
        
        print(f"\n   Medications extracted:")
        print(f"      With examples: {metrics['with_examples']['medications_count']}")
        print(f"      Without examples: {metrics['without_examples']['medications_count']}")
        
        # Show actual outputs
        print("\n" + "="*60)
        print("WITH EXAMPLES - Assessment:")
        print("="*60)
        print(with_examples.get("assessment", "N/A"))
        
        print("\n" + "="*60)
        print("WITHOUT EXAMPLES - Assessment:")
        print("="*60)
        print(without_examples.get("assessment", "N/A"))
        
        print("\n" + "="*60)
        print("WITH EXAMPLES - Plan:")
        print("="*60)
        print(with_examples.get("plan", "N/A")[:300])
        
        print("\n" + "="*60)
        print("WITHOUT EXAMPLES - Plan:")
        print("="*60)
        print(without_examples.get("plan", "N/A")[:300])
        
        # Determine if examples are helping
        improvements = []
        if metrics['with_examples']['objective_length'] > metrics['without_examples']['objective_length']:
            improvements.append("More detailed Objective section")
        if metrics['with_examples']['plan_length'] > metrics['without_examples']['plan_length']:
            improvements.append("More detailed Plan section")
        if metrics['with_examples']['has_icd_codes'] and not metrics['without_examples']['has_icd_codes']:
            improvements.append("ICD codes included")
        if metrics['with_examples']['medications_count'] > metrics['without_examples']['medications_count']:
            improvements.append("Better medication extraction")
        
        print("\n" + "="*60)
        print("VERDICT")
        print("="*60)
        if improvements:
            print("✅ Examples ARE helping!")
            print(f"   Improvements detected: {len(improvements)}")
            for imp in improvements:
                print(f"   - {imp}")
        else:
            print("⚠️  No clear improvements detected")
            print("   This could mean:")
            print("   - Examples need more validation")
            print("   - Need more diverse examples")
            print("   - Test transcript doesn't match example patterns")
        
        return {
            "with_examples": with_examples,
            "without_examples": without_examples,
            "metrics": metrics,
            "improvements": improvements
        }
    
    def test_multiple_transcripts(self, transcripts: List[str], language: str = "en"):
        """Test multiple transcripts and aggregate results"""
        results = []
        improvements_count = 0
        
        for i, transcript in enumerate(transcripts, 1):
            print(f"\n\n{'='*60}")
            print(f"TEST {i}/{len(transcripts)}")
            print(f"{'='*60}")
            result = self.compare_outputs(transcript, language)
            results.append(result)
            if result['improvements']:
                improvements_count += 1
        
        print("\n\n" + "="*60)
        print("AGGREGATE RESULTS")
        print("="*60)
        print(f"Tests run: {len(transcripts)}")
        print(f"Tests showing improvement: {improvements_count}")
        print(f"Success rate: {improvements_count/len(transcripts)*100:.1f}%")
        
        return results


if __name__ == "__main__":
    tester = ExampleLearningTester()
    
    # Test transcripts (use real examples from your dataset)
    test_transcripts = [
        "Patient has fever and cough for 3 days. BP 130/85. Prescribe Paracetamol 650mg three times daily.",
        "Patient complains of abdominal pain for 2 days. Vomiting present. BP 120/80. On examination, tenderness in abdomen.",
        "Patient has headache for 3 days. BP 125/80. Neurological examination normal. Prescribe Paracetamol 500mg SOS."
    ]
    
    print("🧪 Testing Example Learning")
    print(f"📊 Using {len(tester.examples)} validated examples")
    print(f"🧪 Testing {len(test_transcripts)} transcripts\n")
    
    results = tester.test_multiple_transcripts(test_transcripts)
    
    print("\n✅ Testing complete!")
    print("\n💡 Tips:")
    print("   - If improvements are detected, examples are working!")
    print("   - If not, try adding more validated examples")
    print("   - Test with transcripts similar to your examples")

