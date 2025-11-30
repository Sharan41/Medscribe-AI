# Technical Process: Transcript to SOAP Note Generation

**Document:** Technical Implementation Guide  
**Topic:** Converting Transcripts + Medical Entities → SOAP Format  
**Audience:** Beginner Developer (AI/ML concepts explained simply)  
**Date:** November 29, 2024

---

## 🎯 Overview: The Complete Flow

```
Audio Recording
    ↓
Speech-to-Text (Reverie API)
    ↓
Raw Transcript (Tamil/Telugu text)
    ↓
Medical Entity Extraction (Hugging Face NER)
    ↓
Extracted Entities (Symptoms, Medications, Diagnoses, etc.)
    ↓
SOAP Note Generation (Rule-based + Template)
    ↓
Structured SOAP Document
    ↓
Save to Database
```

---

## 📝 Step-by-Step Technical Process

### Step 1: Get Transcript from Reverie API

**What happens:**
- Audio file → Reverie API → Tamil/Telugu text

**Example Output:**
```python
transcript = "நோயாளிக்கு காய்ச்சல் மற்றும் தலைவலி உள்ளது. பாராசிட்டமால் 500mg கொடுக்கவும்."
# Translation: "Patient has fever and headache. Give paracetamol 500mg."
```

**Code Example:**
```python
# From your test script
result = client.asr.stt_file(
    src_lang="ta",  # Tamil
    data=audio_data,
    format="mp3",
    punctuate="true"
)

transcript = result.text  # Get the transcribed text
```

---

### Step 2: Extract Medical Entities (NER)

**What is NER?**
- **NER = Named Entity Recognition**
- **Simple explanation:** Finding important words and labeling them
- **Like:** Highlighting "fever" and tagging it as "SYMPTOM"

**How it works:**
1. Send transcript to medical NER model
2. Model finds medical terms
3. Tags them (SYMPTOM, MEDICATION, DIAGNOSIS, etc.)
4. Returns list of entities

**Example Input:**
```
"நோயாளிக்கு காய்ச்சல் மற்றும் தலைவலி உள்ளது. பாராசிட்டமால் 500mg கொடுக்கவும்."
```

**Example Output (Entities):**
```python
entities = [
    {"word": "காய்ச்சல்", "type": "SYMPTOM", "confidence": 0.95},  # fever
    {"word": "தலைவலி", "type": "SYMPTOM", "confidence": 0.92},  # headache
    {"word": "பாராசிட்டமால்", "type": "MEDICATION", "confidence": 0.98},  # paracetamol
    {"word": "500mg", "type": "DOSAGE", "confidence": 0.99}
]
```

**Code Example:**
```python
from transformers import pipeline

# Load medical NER model
ner = pipeline("ner", 
               model="AventIQ-AI/bert-medical-entity-extraction",
               aggregation_strategy="simple")

# Extract entities from transcript
entities = ner(transcript)

# Result: List of entities with types
```

**Note:** The model might work better with English, so you might need to:
1. Translate Tamil/Telugu → English first
2. Extract entities from English
3. Map back to original language

**Alternative Approach (Rule-based for Tamil/Telugu):**
```python
# Medical term dictionary (Tamil)
MEDICAL_TERMS = {
    "symptoms": {
        "காய்ச்சல்": "fever",
        "தலைவலி": "headache",
        "வயிற்று": "stomach",
        # ... more terms
    },
    "medications": {
        "பாராசிட்டமால்": "paracetamol",
        "அமோக்சிசிலின்": "amoxicillin",
        # ... more terms
    }
}

def extract_entities_rule_based(transcript):
    entities = []
    for category, terms in MEDICAL_TERMS.items():
        for tamil_term, english_term in terms.items():
            if tamil_term in transcript:
                entities.append({
                    "word": tamil_term,
                    "type": category.upper(),
                    "english": english_term
                })
    return entities
```

---

### Step 3: Structure Entities into SOAP Format

**What is SOAP?**
- **S**ubjective: What patient says (complaints, symptoms)
- **O**bjective: What doctor observes (examination findings)
- **A**ssessment: Diagnosis (what doctor thinks)
- **P**lan: Treatment plan (medications, follow-up)

**How to Map Entities to SOAP:**

```python
def map_entities_to_soap(entities, transcript):
    """
    Map extracted entities to SOAP sections
    """
    soap = {
        "subjective": [],  # Patient complaints
        "objective": [],   # Examination findings
        "assessment": [],  # Diagnosis
        "plan": []         # Treatment plan
    }
    
    # Categorize entities
    for entity in entities:
        entity_type = entity["type"]
        word = entity["word"]
        
        if entity_type == "SYMPTOM":
            # Symptoms go to Subjective (patient complaints)
            soap["subjective"].append(word)
        
        elif entity_type == "MEDICATION":
            # Medications go to Plan (treatment)
            soap["plan"].append({
                "medication": word,
                "dosage": entity.get("dosage", ""),
                "frequency": entity.get("frequency", "")
            })
        
        elif entity_type == "DIAGNOSIS":
            # Diagnoses go to Assessment
            soap["assessment"].append(word)
        
        elif entity_type == "VITAL_SIGN":
            # Vital signs go to Objective
            soap["objective"].append({
                "type": entity.get("vital_type"),
                "value": word
            })
    
    return soap
```

**Example Output:**
```python
soap_structure = {
    "subjective": [
        "காய்ச்சல்",      # fever
        "தலைவலி"        # headache
    ],
    "objective": [
        {"type": "temperature", "value": "101°F"},
        {"type": "bp", "value": "120/80"}
    ],
    "assessment": [
        "வைரல் காய்ச்சல்"  # viral fever
    ],
    "plan": [
        {
            "medication": "பாராசிட்டமால்",
            "dosage": "500mg",
            "frequency": "3 times daily"
        },
        {
            "action": "rest",
            "followup": "3 days"
        }
    ]
}
```

---

### Step 4: Generate SOAP Note Document

**Template-Based Approach (Recommended for Beginners):**

```python
def generate_soap_note(soap_structure, patient_info=None):
    """
    Generate formatted SOAP note from structured data
    """
    
    # SOAP Template
    soap_note = f"""
# Medical Consultation Note

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Patient:** {patient_info.get('name', 'N/A') if patient_info else 'N/A'}

---

## Subjective (Patient Complaints)

{format_list(soap_structure['subjective'])}

---

## Objective (Examination Findings)

{format_objective(soap_structure['objective'])}

---

## Assessment (Diagnosis)

{format_list(soap_structure['assessment'])}

---

## Plan (Treatment)

{format_plan(soap_structure['plan'])}

---

**Doctor:** {patient_info.get('doctor_name', 'Dr. Name') if patient_info else 'Dr. Name'}
**Signature:** ________________
"""
    
    return soap_note

def format_list(items):
    """Format list items with bullets"""
    if not items:
        return "- None documented"
    return "\n".join([f"- {item}" for item in items])

def format_objective(objectives):
    """Format objective findings"""
    if not objectives:
        return "- No examination findings documented"
    
    formatted = []
    for obj in objectives:
        if isinstance(obj, dict):
            formatted.append(f"- {obj['type']}: {obj['value']}")
        else:
            formatted.append(f"- {obj}")
    return "\n".join(formatted)

def format_plan(plan_items):
    """Format treatment plan"""
    if not plan_items:
        return "- No treatment plan documented"
    
    formatted = []
    for item in plan_items:
        if isinstance(item, dict):
            if 'medication' in item:
                med = f"- **Medication:** {item['medication']}"
                if item.get('dosage'):
                    med += f" - {item['dosage']}"
                if item.get('frequency'):
                    med += f" ({item['frequency']})"
                formatted.append(med)
            else:
                formatted.append(f"- {item}")
        else:
            formatted.append(f"- {item}")
    return "\n".join(formatted)
```

**Example Output (Final SOAP Note):**
```markdown
# Medical Consultation Note

**Date:** 2024-11-29 14:30
**Patient:** Patient Name

---

## Subjective (Patient Complaints)

- காய்ச்சல் (Fever)
- தலைவலி (Headache)

---

## Objective (Examination Findings)

- Temperature: 101°F
- Blood Pressure: 120/80 mmHg
- General appearance: Appears unwell

---

## Assessment (Diagnosis)

- வைரல் காய்ச்சல் (Viral Fever)

---

## Plan (Treatment)

- **Medication:** பாராசிட்டமால் (Paracetamol) - 500mg (3 times daily)
- Rest and adequate hydration
- Follow-up in 3 days if symptoms persist

---

**Doctor:** Dr. Priya
**Signature:** ________________
```

---

## 🔧 Complete Implementation Example

**Full Pipeline Code:**

```python
from transformers import pipeline
from datetime import datetime
import json

class SOAPNoteGenerator:
    def __init__(self):
        # Initialize NER model
        self.ner = pipeline("ner", 
                           model="AventIQ-AI/bert-medical-entity-extraction",
                           aggregation_strategy="simple")
        
        # Medical term mappings (Tamil)
        self.medical_terms = self.load_medical_terms()
    
    def process_transcript_to_soap(self, transcript, language="ta", patient_info=None):
        """
        Complete pipeline: Transcript → SOAP Note
        """
        # Step 1: Extract entities
        entities = self.extract_entities(transcript, language)
        
        # Step 2: Structure into SOAP
        soap_structure = self.map_to_soap(entities, transcript)
        
        # Step 3: Generate formatted note
        soap_note = self.generate_soap_note(soap_structure, patient_info)
        
        return {
            "soap_note": soap_note,
            "structured_data": soap_structure,
            "entities": entities
        }
    
    def extract_entities(self, transcript, language):
        """
        Extract medical entities from transcript
        """
        # Option 1: Use NER model (if English or translated)
        # Option 2: Use rule-based (for Tamil/Telugu)
        
        if language in ["ta", "te"]:
            # Rule-based extraction for Tamil/Telugu
            return self.extract_rule_based(transcript, language)
        else:
            # Use NER model
            return self.ner(transcript)
    
    def extract_rule_based(self, transcript, language):
        """
        Rule-based entity extraction for Tamil/Telugu
        """
        entities = []
        
        # Load medical dictionaries
        symptoms = self.medical_terms[language]["symptoms"]
        medications = self.medical_terms[language]["medications"]
        
        # Find symptoms
        for term, english in symptoms.items():
            if term in transcript:
                entities.append({
                    "word": term,
                    "type": "SYMPTOM",
                    "english": english
                })
        
        # Find medications
        for term, english in medications.items():
            if term in transcript:
                entities.append({
                    "word": term,
                    "type": "MEDICATION",
                    "english": english
                })
        
        return entities
    
    def map_to_soap(self, entities, transcript):
        """
        Map entities to SOAP structure
        """
        soap = {
            "subjective": [],
            "objective": [],
            "assessment": [],
            "plan": []
        }
        
        for entity in entities:
            entity_type = entity.get("type", "").upper()
            
            if entity_type == "SYMPTOM":
                soap["subjective"].append(entity["word"])
            
            elif entity_type == "MEDICATION":
                soap["plan"].append({
                    "medication": entity["word"],
                    "english": entity.get("english", "")
                })
            
            elif entity_type == "DIAGNOSIS":
                soap["assessment"].append(entity["word"])
        
        return soap
    
    def generate_soap_note(self, soap_structure, patient_info):
        """
        Generate formatted SOAP note
        """
        # Use template-based generation (as shown above)
        return self.format_soap_template(soap_structure, patient_info)
    
    def load_medical_terms(self):
        """
        Load medical term dictionaries
        """
        return {
            "ta": {
                "symptoms": {
                    "காய்ச்சல்": "fever",
                    "தலைவலி": "headache",
                    # ... more
                },
                "medications": {
                    "பாராசிட்டமால்": "paracetamol",
                    # ... more
                }
            },
            "te": {
                # Telugu terms
            }
        }
```

---

## 🎯 Two Approaches: Which to Use?

### Approach 1: NER Model (More Accurate, but English-focused)

**Pros:**
- More accurate entity extraction
- Handles variations better
- Learns from data

**Cons:**
- May need translation Tamil/Telugu → English
- Requires GPU for good performance
- More complex setup

**When to use:**
- If you can translate to English first
- If you have GPU resources
- For production (better accuracy)

### Approach 2: Rule-Based (Simpler, Language-specific)

**Pros:**
- Works directly with Tamil/Telugu
- No translation needed
- Simple to implement
- Fast (no ML model needed)

**Cons:**
- Less flexible (needs dictionary)
- May miss variations
- Requires maintaining dictionaries

**When to use:**
- For MVP (faster to implement)
- If you have good medical dictionaries
- For Tamil/Telugu native support

---

## 💡 Recommended MVP Approach

**Hybrid Approach (Best for MVP):**

1. **Start with Rule-Based:**
   - Create Tamil/Telugu medical dictionaries
   - Simple pattern matching
   - Fast implementation

2. **Add NER Later:**
   - Fine-tune NER model for Tamil/Telugu medical terms
   - Use as enhancement
   - Improve accuracy over time

**Implementation Priority:**
1. ✅ Rule-based extraction (Week 1-2)
2. ✅ Template-based SOAP generation (Week 2-3)
3. 🔄 NER model integration (Week 4-5)
4. 🔄 Fine-tuning for Tamil/Telugu (Phase 2)

---

## 📊 Example: Complete Flow

**Input:**
```
Audio: Doctor speaking Tamil
"நோயாளிக்கு காய்ச்சல் மற்றும் தலைவலி உள்ளது. 
பாராசிட்டமால் 500mg மூன்று முறை கொடுக்கவும்."
```

**Step 1: Transcription (Reverie API)**
```
Transcript: "நோயாளிக்கு காய்ச்சல் மற்றும் தலைவலி உள்ளது. 
பாராசிட்டமால் 500mg மூன்று முறை கொடுக்கவும்."
```

**Step 2: Entity Extraction**
```python
entities = [
    {"word": "காய்ச்சல்", "type": "SYMPTOM"},
    {"word": "தலைவலி", "type": "SYMPTOM"},
    {"word": "பாராசிட்டமால்", "type": "MEDICATION", "dosage": "500mg", "frequency": "3 times"}
]
```

**Step 3: SOAP Structure**
```python
soap = {
    "subjective": ["காய்ச்சல்", "தலைவலி"],
    "objective": [],
    "assessment": [],
    "plan": [{"medication": "பாராசிட்டமால்", "dosage": "500mg", "frequency": "3 times daily"}]
}
```

**Step 4: Formatted SOAP Note**
```markdown
## Subjective
- காய்ச்சல் (Fever)
- தலைவலி (Headache)

## Plan
- பாராசிட்டமால் 500mg (3 times daily)
```

---

## 🚀 Next Steps

1. **Create Medical Dictionaries:**
   - Tamil symptoms dictionary
   - Tamil medications dictionary
   - Telugu dictionaries

2. **Implement Rule-Based Extractor:**
   - Pattern matching code
   - Dictionary lookup

3. **Create SOAP Template:**
   - Template structure
   - Formatting functions

4. **Test with Real Transcripts:**
   - Test with doctor consultations
   - Refine extraction rules
   - Improve templates

---

**This approach is beginner-friendly and gets you started quickly!** 🎉

