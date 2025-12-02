"""
Script to collect and organize Indian clinical examples for SOAP generation
"""
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ExampleCollector:
    def __init__(self):
        self.examples_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "indian_clinical_examples.json"
        )
        self.examples = self._load_examples()
    
    def _load_examples(self) -> Dict:
        """Load existing examples"""
        try:
            with open(self.examples_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "examples": [],
                "categories": {},
                "metadata": {
                    "total_examples": 0,
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
    
    def add_from_database(self, consultation_id: str, transcript: str, 
                         soap_note: Dict, language: str, validated: bool = False):
        """Add example from database consultation"""
        example = {
            "id": f"db_{consultation_id}",
            "condition_type": self._classify_condition(soap_note),
            "language": language,
            "transcript": transcript,
            "soap_note": {
                "subjective": soap_note.get("subjective", ""),
                "objective": soap_note.get("objective", ""),
                "assessment": soap_note.get("assessment", ""),
                "plan": soap_note.get("plan", "")
            },
            "entities": soap_note.get("entities", {}),
            "icd_codes": soap_note.get("icd_codes", []),
            "source": "database",
            "validated": validated,
            "date": datetime.now().isoformat()
        }
        self.examples["examples"].append(example)
        self._save_examples()
        return example
    
    def add_synthetic(self, transcript: str, transcript_english: str,
                      soap_note: Dict, language: str, validated: bool = False):
        """Add synthetic example"""
        example = {
            "id": f"synth_{len(self.examples['examples'])}",
            "condition_type": self._classify_condition(soap_note),
            "language": language,
            "transcript": transcript,
            "transcript_english": transcript_english,
            "soap_note": {
                "subjective": soap_note.get("subjective", ""),
                "objective": soap_note.get("objective", ""),
                "assessment": soap_note.get("assessment", ""),
                "plan": soap_note.get("plan", "")
            },
            "entities": soap_note.get("entities", {}),
            "icd_codes": soap_note.get("icd_codes", []),
            "source": "synthetic",
            "validated": validated,
            "date": datetime.now().isoformat()
        }
        self.examples["examples"].append(example)
        self._save_examples()
        return example
    
    def _classify_condition(self, soap_note: Dict) -> str:
        """Classify condition type from SOAP note"""
        assessment = soap_note.get("assessment", "").lower()
        
        if any(term in assessment for term in ["fever", "cough", "respiratory", "pneumonia", "urti", "bronchitis"]):
            return "respiratory"
        elif any(term in assessment for term in ["abdominal", "gastritis", "diarrhea", "stomach", "gastro"]):
            return "gastrointestinal"
        elif any(term in assessment for term in ["hypertension", "heart", "cardiac", "chest pain", "cardiovascular"]):
            return "cardiovascular"
        elif any(term in assessment for term in ["headache", "seizure", "neurological", "tension"]):
            return "neurological"
        elif any(term in assessment for term in ["joint", "muscle", "back pain", "arthritis", "musculoskeletal"]):
            return "musculoskeletal"
        elif any(term in assessment for term in ["diabetes", "thyroid", "hormone", "endocrine", "diabetic"]):
            return "endocrine"
        elif any(term in assessment for term in ["rash", "skin", "dermatological", "dermatitis"]):
            return "dermatological"
        else:
            return "general"
    
    def _save_examples(self):
        """Save examples to file"""
        # Update category counts
        categories = {}
        for ex in self.examples["examples"]:
            cat = ex["condition_type"]
            categories[cat] = categories.get(cat, 0) + 1
        
        self.examples["categories"] = categories
        self.examples["metadata"] = {
            "total_examples": len(self.examples["examples"]),
            "last_updated": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.examples_file), exist_ok=True)
        
        with open(self.examples_file, 'w', encoding='utf-8') as f:
            json.dump(self.examples, f, indent=2, ensure_ascii=False)
    
    def get_examples_by_category(self, category: str, limit: int = 5) -> List[Dict]:
        """Get examples by category"""
        return [
            ex for ex in self.examples["examples"]
            if ex["condition_type"] == category and ex.get("validated", False)
        ][:limit]
    
    def get_all_examples(self, limit: int = 20, validated_only: bool = True) -> List[Dict]:
        """Get all examples"""
        examples = self.examples["examples"]
        if validated_only:
            examples = [ex for ex in examples if ex.get("validated", False)]
        return examples[:limit]
    
    def get_few_shot_examples(self, condition_type: Optional[str] = None, count: int = 3) -> List[Dict]:
        """Get examples for few-shot learning"""
        if condition_type:
            return self.get_examples_by_category(condition_type, limit=count)
        else:
            # Get diverse examples from different categories
            categories = list(set(ex["condition_type"] for ex in self.examples["examples"]))
            examples = []
            for cat in categories[:count]:
                cat_examples = self.get_examples_by_category(cat, limit=1)
                examples.extend(cat_examples)
            return examples[:count]


if __name__ == "__main__":
    collector = ExampleCollector()
    
    print(f"Loaded {len(collector.examples['examples'])} examples")
    print(f"Categories: {collector.examples['categories']}")
    
    # Example usage
    print("\nExample: Get respiratory examples")
    resp_examples = collector.get_examples_by_category("respiratory", limit=2)
    for ex in resp_examples:
        print(f"- {ex['id']}: {ex['soap_note']['assessment']}")

