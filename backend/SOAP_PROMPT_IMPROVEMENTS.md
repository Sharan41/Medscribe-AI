# SOAP Note Generation Prompt Improvements

## Overview
Enhanced the Groq prompt for SOAP note generation based on professional medical scribe documentation standards and Indian medical practice conventions.

## Key Improvements

### 1. **Professional System Prompt**
- Enhanced role definition as "expert medical scribe AI assistant"
- Emphasis on professional medical documentation standards
- Focus on Indian medical practice conventions
- Clear documentation standards and best practices

### 2. **Detailed Instructions**
- **Subjective Section:**
  - Clear documentation of chief complaints with duration
  - Relevant history capture
  - Proper formatting with Tamil/Telugu terms in brackets
  
- **Objective Section:**
  - Comprehensive vital signs documentation (BP, pulse, temp, SpO2, RR)
  - Physical examination findings
  - Lab values and test results
  - Proper units (mmHg, bpm, °C)
  
- **Assessment Section:**
  - Standard medical terminology
  - ICD-10 compatible diagnoses
  - Severity/stage documentation
  
- **Plan Section:**
  - Complete medication details:
    * Generic name (brand if mentioned)
    * Dosage (e.g., 500mg, 650mg)
    * Frequency (TID, BD, OD, SOS)
    * Duration (e.g., for 5 days, 1 week)
  - Lifestyle modifications
  - Clear follow-up instructions
  - Referrals and investigations

### 3. **Professional Examples**
- Real-world consultation examples
- Proper JSON format demonstration
- Complete medication documentation
- Follow-up instructions
- Tamil/Telugu term integration

### 4. **Model Upgrade**
- Changed from `llama-3.1-8b-instant` to `llama-3.1-70b-versatile`
- Better understanding and quality
- More professional output
- Improved medical terminology accuracy

### 5. **Temperature Adjustment**
- Increased from 0.1 to 0.2
- Better balance between consistency and quality
- More natural medical language
- Still maintains accuracy

### 6. **Token Limit**
- Increased from 2000 to 2500 tokens
- Allows for more comprehensive notes
- Better detail in all sections

## Comparison: Before vs After

### Before:
- Basic prompt with minimal instructions
- Simple examples
- Focus on JSON output format
- Limited medical terminology guidance

### After:
- Professional medical scribe system prompt
- Detailed section-by-section instructions
- Real-world examples with complete documentation
- Emphasis on professional medical standards
- Better medication documentation
- Clear follow-up instructions
- Indian medical practice conventions

## Expected Improvements

1. **Better Structure:** More consistent SOAP note formatting
2. **Complete Information:** All vital signs, medications, and findings captured
3. **Professional Language:** Standard medical terminology throughout
4. **Better Medications:** Complete dosage, frequency, and duration information
5. **Clear Follow-ups:** Specific follow-up instructions with timelines
6. **Indian Context:** Appropriate for Indian medical practice

## Usage

The improved prompt is automatically used when generating SOAP notes. No code changes needed in the API endpoints - the service handles everything internally.

## Testing

To test the improvements:
1. Generate a SOAP note from a consultation
2. Verify all sections are complete
3. Check medication details (dosage, frequency, duration)
4. Verify follow-up instructions are clear
5. Confirm professional medical language is used

## Files Modified

- `backend/app/services/soap_service.py`
  - Added `_get_system_prompt()` method
  - Added `_create_professional_prompt()` method
  - Added `_get_professional_examples()` method
  - Updated model to `llama-3.1-70b-versatile`
  - Increased max_tokens to 2500
  - Adjusted temperature to 0.2

## Next Steps

1. Test with real consultations
2. Gather feedback from doctors
3. Fine-tune examples based on actual usage
4. Consider adding specialty-specific prompts (cardiology, pediatrics, etc.)

