"""
Integrate EkaCare Medical ASR Dataset into SOAP examples
Converts medical transcripts to SOAP note examples for few-shot learning
"""
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add project root and backend to path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

try:
    from datasets import load_dataset
    DATASETS_AVAILABLE = True
    # Keep load_dataset in global scope
    _load_dataset = load_dataset
except ImportError:
    DATASETS_AVAILABLE = False
    _load_dataset = None
    print("Warning: datasets library not installed. Run: pip install datasets")

try:
    import google.generativeai as genai
    # Try to import settings, but handle if not available
    try:
        from app.config import settings
        SETTINGS_AVAILABLE = True
    except ImportError:
        SETTINGS_AVAILABLE = False
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    SETTINGS_AVAILABLE = False
    print("Warning: Gemini not available. Check imports.")

# Import ExampleCollector - import directly from same directory
import importlib.util
spec = importlib.util.spec_from_file_location("collect_examples", os.path.join(script_dir, "collect_examples.py"))
collect_examples = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect_examples)
ExampleCollector = collect_examples.ExampleCollector

class EkaDatasetIntegrator:
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize integrator"""
        if not DATASETS_AVAILABLE:
            raise ImportError("datasets library required. Install with: pip install datasets")
        
        if not GEMINI_AVAILABLE:
            raise ImportError("Gemini not available. Check configuration.")
        
        # Initialize Gemini - try multiple sources for API key
        api_key = gemini_api_key
        
        if not api_key and SETTINGS_AVAILABLE:
            api_key = settings.GEMINI_API_KEY
        
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        
        # Try loading from .env file if still not found
        if not api_key:
            env_file = os.path.join(backend_dir, ".env")
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r') as f:
                        for line in f:
                            if line.startswith("GEMINI_API_KEY="):
                                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                                break
                except Exception:
                    pass
        
        if not api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY environment variable, "
                "add to backend/.env file, or pass gemini_api_key parameter."
            )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            "models/gemini-2.0-flash",
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 4000,
            }
        )
        
        # Initialize collector
        self.collector = ExampleCollector()
        
        # Load dataset - try multiple methods
        print("Loading EkaCare dataset...")
        if not DATASETS_AVAILABLE or _load_dataset is None:
            raise ImportError("datasets library required. Install with: pip install datasets")
        
        try:
            # Method 1: Try loading directly with split, select only text columns
            print("   Method 1: Loading with split='test' (text only)...")
            # Load dataset first
            dataset_temp = _load_dataset(
                'ekacare/eka-medical-asr-evaluation-dataset', 
                'en', 
                split='test'
            )
            # Select only text columns, exclude audio
            text_columns = [col for col in dataset_temp.column_names if col != 'audio']
            self.dataset_en = dataset_temp.select_columns(text_columns)
            print(f"✅ Loaded {len(self.dataset_en)} English samples")
        except Exception as e:
            print(f"   Method 1 failed: {e}")
            print("\n   Method 2: Loading all splits...")
            try:
                # Method 2: Load all splits first, then select text columns
                dataset_all = _load_dataset(
                    'ekacare/eka-medical-asr-evaluation-dataset',
                    'en'
                )
                print(f"   Available splits: {list(dataset_all.keys())}")
                
                # Get test split
                if 'test' in dataset_all:
                    dataset_temp = dataset_all['test']
                else:
                    # Use whatever split is available
                    split_name = list(dataset_all.keys())[0]
                    dataset_temp = dataset_all[split_name]
                    print(f"   Using split: {split_name}")
                
                # Select only text columns, exclude audio
                text_columns = [col for col in dataset_temp.column_names if col != 'audio']
                self.dataset_en = dataset_temp.select_columns(text_columns)
                print(f"✅ Loaded {len(self.dataset_en)} English samples")
            except Exception as e2:
                print(f"   Method 2 failed: {e2}")
                print("\n   Method 3: Trying with streaming (text only, no audio)...")
                try:
                    # Method 3: Try streaming mode - MUST select columns BEFORE iterating
                    print("   Loading streaming dataset...")
                    dataset_stream = _load_dataset(
                        'ekacare/eka-medical-asr-evaluation-dataset',
                        'en',
                        split='test',
                        streaming=True
                    )
                    # CRITICAL: Select columns BEFORE iterating to avoid audio decoding
                    text_columns = ['text', 'medical_entities', 'type_concept', 'recording_context', 
                                   'session_id', 'speaker', 'audio_language', 'duration', 
                                   'md5_text', 'file_name', 'md5_audio', 'text_language']
                    # Filter to only columns that exist
                    available_cols = []
                    try:
                        # Try to get column names from first sample (without decoding audio)
                        first_sample = next(iter(dataset_stream))
                        available_cols = [col for col in text_columns if col in first_sample and col != 'audio']
                        # Reset iterator
                        dataset_stream = _load_dataset(
                            'ekacare/eka-medical-asr-evaluation-dataset',
                            'en',
                            split='test',
                            streaming=True
                        )
                    except:
                        # Fallback: use known text columns
                        available_cols = [col for col in text_columns if col != 'audio']
                    
                    # Select only text columns
                    dataset_stream = dataset_stream.select_columns(available_cols)
                    
                    # Convert streaming dataset to list (take first 100 for testing)
                    print("   Converting to list (text only)...")
                    samples = []
                    for i, sample in enumerate(dataset_stream):
                        if i >= 100:  # Limit for testing
                            break
                        samples.append(dict(sample))  # Convert to regular dict
                    
                    # Create a simple dataset-like object
                    class SimpleDataset:
                        def __init__(self, samples):
                            self.samples = samples
                        def __len__(self):
                            return len(self.samples)
                        def __getitem__(self, idx):
                            return self.samples[idx]
                        def __iter__(self):
                            return iter(self.samples)
                    self.dataset_en = SimpleDataset(samples)
                    print(f"✅ Loaded {len(self.dataset_en)} samples (streaming mode, text only)")
                except Exception as e3:
                    error_msg = str(e3)
                    print(f"   Method 3 failed: {e3}")
                    print("\n❌ All loading methods failed")
                    
                    # Check if it's an access permission issue
                    if "403" in error_msg or "Forbidden" in error_msg or "gated" in error_msg.lower():
                        print("\n🔒 DATASET ACCESS REQUIRED:")
                        print("   This dataset is gated and requires special permissions.")
                        print("   Steps to get access:")
                        print("   1. Visit: https://huggingface.co/datasets/ekacare/eka-medical-asr-evaluation-dataset")
                        print("   2. Click 'Request access' button")
                        print("   3. Wait for approval (usually a few hours)")
                        print("   4. Re-run this script after approval")
                        print("\n   See DATASET_ACCESS_REQUIRED.md for detailed instructions")
                    else:
                        print("\n💡 Troubleshooting:")
                        print("   1. Check internet connection")
                        print("   2. Clear cache: rm -rf ~/.cache/huggingface/")
                        print("   3. Try: huggingface-cli login")
                        print("   4. Verify dataset: https://huggingface.co/datasets/ekacare/eka-medical-asr-evaluation-dataset")
                    raise
    
    def extract_transcript_data(self, sample: Dict) -> Dict:
        """Extract relevant data from dataset sample"""
        return {
            "transcript": sample.get("text", ""),
            "medical_entities": sample.get("medical_entities", ""),
            "type_concept": sample.get("type_concept", ""),
            "recording_context": sample.get("recording_context", ""),
            "session_id": sample.get("session_id", ""),
            "speaker": sample.get("speaker", ""),
            "language": sample.get("audio_language", "en"),
            "duration": sample.get("duration", 0)
        }
    
    def generate_soap_from_transcript(self, transcript: str, medical_entities: str = "") -> Optional[Dict]:
        """Generate SOAP note from transcript using Gemini"""
        
        prompt = f"""Convert this medical consultation transcript into a structured SOAP note following Indian medical documentation standards.

Transcript: {transcript}

{f'Medical Entities (if available): {medical_entities}' if medical_entities else ''}

Generate a complete SOAP note with:
- Subjective: Patient complaints with duration
- Objective: Vital signs, physical examination findings (infer common examinations if symptoms mentioned but not documented)
- Assessment: Primary diagnosis using standard medical terminology with ICD-10 code
- Plan: Medications with dosage, frequency (TID/BD/OD/SOS), duration, and follow-up instructions

Output as JSON only:
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

All output must be in English. Use standard medical terminology. Output ONLY valid JSON, no additional text."""
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Try to parse JSON
            try:
                soap_note = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    soap_note = json.loads(json_match.group(1))
                else:
                    # Try to find JSON object in text
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        soap_note = json.loads(json_match.group(0))
                    else:
                        raise ValueError("Could not parse JSON from response")
            
            # Validate structure
            required_fields = ["subjective", "objective", "assessment", "plan"]
            if not all(field in soap_note for field in required_fields):
                raise ValueError("Missing required SOAP fields")
            
            return soap_note
            
        except Exception as e:
            print(f"   ⚠️  Error generating SOAP: {e}")
            return None
    
    def process_samples(self, num_samples: int = 50, start_index: int = 0, 
                       min_transcript_length: int = 50):
        """Process samples from dataset and add to examples"""
        
        processed = 0
        added = 0
        skipped = 0
        
        # Handle both regular and streaming datasets
        dataset_len = len(self.dataset_en) if hasattr(self.dataset_en, '__len__') else num_samples
        max_samples = min(start_index + num_samples, dataset_len) if dataset_len else start_index + num_samples
        
        print(f"\n🚀 Processing {num_samples} samples (starting from index {start_index})...")
        
        # Handle iteration for both regular and streaming datasets
        if hasattr(self.dataset_en, '__iter__') and not hasattr(self.dataset_en, '__getitem__'):
            # Streaming dataset - iterate directly
            iterator = iter(self.dataset_en)
            for _ in range(start_index):
                next(iterator, None)  # Skip to start_index
            
            for i in range(num_samples):
                try:
                    sample = next(iterator)
                except StopIteration:
                    break
                processed += 1
                self._process_single_sample(sample, i + start_index, processed, added, skipped, min_transcript_length)
                added, skipped = self._get_counts()
        else:
            # Regular dataset - use indexing
            for i in range(start_index, max_samples):
                sample = self.dataset_en[i]
                processed += 1
                added, skipped = self._process_single_sample(sample, i, processed, added, skipped, min_transcript_length)
        
        print(f"\n📊 Summary:")
        print(f"   Processed: {processed}")
        print(f"   Added: {added}")
        print(f"   Skipped (too short): {skipped}")
        
        return added
    
    def _process_single_sample(self, sample, index, processed, added, skipped, min_transcript_length):
        """Process a single sample"""
        transcript_data = self.extract_transcript_data(sample)
        
        # Skip very short transcripts
        if len(transcript_data["transcript"]) < min_transcript_length:
            skipped += 1
            return added, skipped
        
        session_id = transcript_data.get("session_id", f"sample_{index}")
        transcript_preview = transcript_data["transcript"][:80] + "..." if len(transcript_data["transcript"]) > 80 else transcript_data["transcript"]
        
        print(f"\n[{processed}] {session_id}")
        print(f"   Transcript: {transcript_preview}")
        
        # Generate SOAP note
        soap_note = self.generate_soap_from_transcript(
            transcript_data["transcript"],
            transcript_data.get("medical_entities", "")
        )
        
        if soap_note:
            # Add to examples
            try:
                self.collector.add_synthetic(
                    transcript=transcript_data["transcript"],
                    transcript_english=transcript_data["transcript"],
                    soap_note=soap_note,
                    language="en",
                    validated=False  # Mark for doctor review
                )
                added += 1
                print(f"   ✅ Added example {added}")
            except Exception as e:
                print(f"   ❌ Failed to add example: {e}")
        else:
            print(f"   ❌ Failed to generate SOAP")
        
        return added, skipped
    
    def _get_counts(self):
        """Helper to get current counts - placeholder"""
        return 0, 0
        print(f"   Skipped (too short): {skipped}")
        
        return added
    
    def filter_by_context(self, context_type: str = "conversation") -> List[Dict]:
        """Filter samples by recording context"""
        filtered = []
        for sample in self.dataset_en:
            if sample.get("recording_context", "") == context_type:
                filtered.append(self.extract_transcript_data(sample))
        return filtered
    
    def filter_by_concept_type(self, concept_type: str) -> List[Dict]:
        """Filter samples by medical concept type"""
        filtered = []
        for sample in self.dataset_en:
            if sample.get("type_concept", "") == concept_type:
                filtered.append(self.extract_transcript_data(sample))
        return filtered
    
    def get_dataset_stats(self):
        """Get statistics about the dataset"""
        stats = {
            "total_samples": len(self.dataset_en),
            "contexts": {},
            "concept_types": {},
            "avg_transcript_length": 0,
            "samples_with_entities": 0
        }
        
        total_length = 0
        for sample in self.dataset_en:
            context = sample.get("recording_context", "unknown")
            stats["contexts"][context] = stats["contexts"].get(context, 0) + 1
            
            concept = sample.get("type_concept", "unknown")
            stats["concept_types"][concept] = stats["concept_types"].get(concept, 0) + 1
            
            transcript = sample.get("text", "")
            total_length += len(transcript)
            
            if sample.get("medical_entities"):
                stats["samples_with_entities"] += 1
        
        stats["avg_transcript_length"] = total_length / len(self.dataset_en) if self.dataset_en else 0
        
        return stats


if __name__ == "__main__":
    print("=" * 60)
    print("EkaCare Medical ASR Dataset Integration")
    print("=" * 60)
    
    try:
        # Initialize integrator
        integrator = EkaDatasetIntegrator()
        
        # Show dataset stats
        print("\n📊 Dataset Statistics:")
        stats = integrator.get_dataset_stats()
        print(f"   Total samples: {stats['total_samples']}")
        print(f"   Average transcript length: {stats['avg_transcript_length']:.0f} chars")
        print(f"   Samples with entities: {stats['samples_with_entities']}")
        print(f"\n   Recording contexts:")
        for context, count in stats['contexts'].items():
            print(f"     - {context}: {count}")
        
        # Process first 10 samples (start small for testing)
        print("\n🚀 Starting integration...")
        num_samples = 10  # Start with 10 samples for testing
        added = integrator.process_samples(num_samples=num_samples, start_index=0)
        
        print(f"\n✅ Integration complete! Added {added} examples to database.")
        print(f"\n📊 Processed {num_samples} samples, successfully added {added} SOAP examples")
        print("\n📝 Next steps:")
        print("   1. Review examples in backend/data/indian_clinical_examples.json")
        print("   2. Check quality of generated SOAP notes")
        print("   3. Get doctors to validate examples")
        print("   4. Mark validated examples (set validated=True)")
        print("   5. Process more samples: Change num_samples=50 or num_samples=100")
        print("\n💡 Tip: Focus on 'conversation' context samples for best SOAP examples")
        print(f"💡 To process more: Edit num_samples in script (currently set to {num_samples})")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Install dependencies: pip install datasets huggingface_hub")
        print("   2. Login to Hugging Face: huggingface-cli login")
        print("   3. Check GEMINI_API_KEY is set")
        sys.exit(1)

