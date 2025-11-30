# Phase 1: Getting Started Guide - For ML Beginners

**Welcome!** This guide will help you complete Phase 1 (Analysis & Research) step-by-step, with simple explanations of ML concepts.

---

## 🎯 What We're Doing in Phase 1

**Goal:** Research and understand what we need to build MedScribe AI

**You'll Learn:**
- How speech-to-text works (simply)
- How to use APIs (no ML coding needed yet)
- What medical NLP means
- How to test different solutions

**Time:** 1-2 weeks (but you can go faster!)

---

## 📚 Step 1: Understand the Basics (30 minutes)

### Read These First:

1. **Domain Research Document:** `docs/sprint-artifacts/domain-research-medical-scribe.md`
   - Explains ML concepts simply
   - Lists all technology options
   - Tells you what accounts to create

2. **Key ML Concepts (Quick Summary):**

   **Speech-to-Text:**
   - Audio file → Text file
   - Like Siri understanding you
   - We'll use an API (like calling a function)

   **Entity Extraction:**
   - Text → Important words tagged
   - "Patient has fever" → [fever = SYMPTOM]
   - We'll use a pre-trained model (already knows medical terms)

   **Fine-tuning:**
   - Teaching a model new examples
   - Like training a new employee with examples
   - We'll do this later if needed

---

## 🔧 Step 2: Set Up Your Development Environment (1 hour)

### Install Python

1. **Download Python:**
   - Go to [python.org](https://www.python.org/downloads/)
   - Download Python 3.11 or newer
   - Install it (check "Add Python to PATH")

2. **Verify Installation:**
   ```bash
   python --version
   # Should show: Python 3.11.x or similar
   ```

3. **Create Project Folder:**
   ```bash
   mkdir medscribe-app
   cd medscribe-app
   ```

4. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   
   # Activate it:
   # On Mac/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

5. **Install Basic Libraries:**
   ```bash
   pip install fastapi uvicorn requests
   ```

**What's a virtual environment?**
- **Simple explanation:** Isolated Python environment for your project
- **Why:** Keeps your project's libraries separate from other projects
- **Like:** A separate toolbox for this project

---

## 🎤 Step 3: Test Speech-to-Text APIs (2-3 hours)

### Option A: Test Reverie API (Recommended First)

**Why Start Here:**
- Easiest to use
- Works immediately
- No ML knowledge needed

**Steps:**

1. **Sign Up:**
   - Go to [Reverie Website](https://reverieinc.com/products/speech-to-text-api/)
   - Sign up for account
   - Get API key and App ID

2. **Install SDK:**
   ```bash
   pip install reverie-sdk
   ```

3. **Create Test Script:**
   Create file `test_reverie.py`:
   ```python
   from reverie_sdk import ReverieClient
   
   # Replace with your actual credentials
   API_KEY = "your_api_key_here"
   APP_ID = "your_app_id_here"
   
   # Create client
   client = ReverieClient(api_key=API_KEY, app_id=APP_ID)
   
   # Read audio file (you'll need to record one)
   with open("test_audio.wav", "rb") as f:
       audio_data = f.read()
   
   # Convert speech to text
   result = client.asr.stt_file(
       src_lang="hi",  # "hi" = Hindi, "ta" = Tamil, "te" = Telugu
       data=audio_data,
       punctuate=True
   )
   
   print("Transcribed text:", result['text'])
   ```

4. **Record Test Audio:**
   - Use your phone to record 10 seconds of Hindi speech
   - Say something like: "मरीज़ को बुखार है और सिर दर्द हो रहा है"
   - Save as `test_audio.wav` (or convert to WAV format)
   - Put in same folder as `test_reverie.py`

5. **Run Test:**
   ```bash
   python test_reverie.py
   ```

6. **Check Results:**
   - Did it transcribe correctly?
   - How long did it take?
   - Note accuracy and speed

**Troubleshooting:**
- **Error: "Invalid API key"** → Check your credentials
- **Error: "File not found"** → Check audio file path
- **Error: "Unsupported format"** → Convert audio to WAV format

---

### Option B: Test OpenAI Whisper (Free Alternative)

**Why Test This:**
- Free to use
- Good accuracy
- Can run offline (after setup)

**Steps:**

1. **Install Whisper:**
   ```bash
   pip install openai-whisper
   ```

2. **Create Test Script:**
   Create file `test_whisper.py`:
   ```python
   import whisper
   
   # Load model (downloads automatically first time)
   # "base" is smallest, "large" is most accurate but slower
   model = whisper.load_model("base")
   
   # Transcribe audio
   result = model.transcribe("test_audio.wav", language="hi")
   
   print("Transcribed text:", result["text"])
   ```

3. **Run Test:**
   ```bash
   python test_whisper.py
   ```
   - First run will download model (takes a few minutes)
   - Subsequent runs are faster

4. **Compare Results:**
   - Compare accuracy with Reverie
   - Note: Whisper may need fine-tuning for Indian medical terms

**What's a "model"?**
- **Simple explanation:** A file containing learned patterns
- **Like:** A dictionary that knows how to convert sounds to words
- **Sizes:** base (smaller, faster) vs large (bigger, more accurate)

---

## 🧠 Step 4: Test Medical Entity Extraction (1-2 hours)

**Goal:** Extract medical terms from text

**Steps:**

1. **Sign Up for Hugging Face:**
   - Go to [huggingface.co](https://huggingface.co)
   - Create free account
   - Get access token (Settings → Access Tokens)

2. **Install Libraries:**
   ```bash
   pip install transformers torch
   ```

3. **Create Test Script:**
   Create file `test_entity_extraction.py`:
   ```python
   from transformers import pipeline
   
   # Load medical entity extraction model
   # This downloads the model first time (takes a few minutes)
   ner = pipeline("ner", 
                  model="AventIQ-AI/bert-medical-entity-extraction",
                  aggregation_strategy="simple")
   
   # Test with English medical text
   text = "Patient has fever and headache. Prescribe paracetamol 500mg."
   
   # Extract entities
   entities = ner(text)
   
   print("Extracted entities:")
   for entity in entities:
       print(f"- {entity['word']}: {entity['entity_group']}")
   ```

4. **Run Test:**
   ```bash
   python test_entity_extraction.py
   ```

5. **Expected Output:**
   ```
   Extracted entities:
   - fever: SYMPTOM
   - headache: SYMPTOM
   - paracetamol: MEDICATION
   ```

**What's "NER"?**
- **NER = Named Entity Recognition**
- **Simple explanation:** Finding important words and labeling them
- **Like:** Highlighting key terms in a document

**Note:** This model works best with English. For Hindi, we'll need to:
- Translate Hindi → English first, OR
- Find/fine-tune a Hindi medical model

---

## 📊 Step 5: Compare Results (30 minutes)

### Create Comparison Table

Create file `api_comparison.md`:

```markdown
# API Comparison Results

## Reverie API
- Accuracy: [Your rating 1-5]
- Speed: [Fast/Medium/Slow]
- Ease of use: [Easy/Medium/Hard]
- Cost: [Free/Paid]
- Notes: [Any observations]

## Whisper
- Accuracy: [Your rating 1-5]
- Speed: [Fast/Medium/Slow]
- Ease of use: [Easy/Medium/Hard]
- Cost: Free
- Notes: [Any observations]

## Recommendation
[Which one should we use for MVP?]
```

---

## 🎯 Step 6: Research Competitive Solutions (2-3 hours)

### Find Competitors

1. **Search Terms:**
   - "medical scribe India"
   - "voice to text medical notes India"
   - "AI medical transcription India"

2. **For Each Competitor, Note:**
   - Features they offer
   - Pricing
   - Languages supported
   - What they do well
   - What they're missing (our opportunity!)

3. **Create Competitive Analysis:**
   Create file `competitive-analysis.md`:
   ```markdown
   # Competitive Analysis
   
   ## Competitor 1: [Name]
   - Features: [List]
   - Pricing: [Amount]
   - Languages: [List]
   - Strengths: [List]
   - Weaknesses: [List]
   
   ## Our Differentiation
   - [What makes us different]
   ```

---

## ✅ Step 7: Complete Research Checklist

### Review Domain Research Document

Go through `docs/sprint-artifacts/domain-research-medical-scribe.md` and check:

- [ ] Understand DPDP Act requirements
- [ ] Understand ABDM/FHIR basics
- [ ] Tested Reverie API
- [ ] Tested Whisper
- [ ] Tested Hugging Face entity extraction
- [ ] Created API comparison
- [ ] Researched competitors
- [ ] Created competitive analysis

---

## 🚀 Step 8: Prepare for Phase 2

### What You Should Have:

1. **Test Results:**
   - Which speech-to-text API works best?
   - Which entity extraction works?
   - What are the limitations?

2. **Accounts Created:**
   - Reverie API (if using)
   - Hugging Face
   - ABDM Sandbox

3. **Understanding:**
   - How speech-to-text works (simply)
   - How entity extraction works (simply)
   - What regulations apply
   - Who competitors are

---

## 💡 Common Questions (FAQ)

### Q: Do I need to understand ML deeply?
**A:** No! You're using APIs and pre-trained models. Think of them as libraries you call, not code you write.

### Q: What if APIs don't work well?
**A:** That's okay! We'll try alternatives or improve them later. The goal is to get something working first.

### Q: How do I know which API to choose?
**A:** Test both, compare accuracy and ease of use. Start with the easiest (Reverie), improve later.

### Q: What if I get errors?
**A:** 
- Check error messages carefully
- Google the error (someone else had it!)
- Ask for help (I'm here!)
- Try simpler examples first

### Q: How long should Phase 1 take?
**A:** 1-2 weeks if you're learning. But you can go faster if you're experienced. Don't rush - understanding is important!

---

## 🎓 Learning Path

### This Week:
1. ✅ Read domain research
2. ✅ Set up Python environment
3. ✅ Test Reverie API
4. ✅ Test Whisper

### Next Week:
1. ✅ Test entity extraction
2. ✅ Research competitors
3. ✅ Create comparison documents
4. ✅ Prepare for Phase 2

---

## 📝 Next Steps After Phase 1

Once you complete Phase 1:

1. **Move to Phase 2:** Product Planning
   - Create Product Brief
   - Create PRD (Product Requirements Document)
   - Create User Stories

2. **You'll Use:**
   - PM Agent for product planning
   - UX Designer for interface design

---

## 🆘 Need Help?

**If you're stuck:**
1. Check error messages carefully
2. Google the error
3. Ask me (the Analyst agent) for help
4. Check documentation links in domain research

**Remember:** 
- It's okay to not understand everything immediately
- Learning happens by doing
- Start simple, improve later
- You're building something awesome! 🚀

---

**Good luck with Phase 1!** You've got this! 💪

