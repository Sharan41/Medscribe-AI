# Product Requirements Document (PRD): MedScribe AI

**Document Type:** Product Requirements Document  
**Project:** MedScribe AI - Indian Medical Transcription Assistant  
**Version:** 1.0  
**Date:** November 29, 2024  
**Author:** PM Agent (BMAD Methodology)  
**Status:** Draft → Ready for Architecture

---

## 📋 Document Information

- **Product Name:** MedScribe AI
- **Product Manager:** PM Agent
- **Stakeholders:** Development Team, Doctors, Clinic Administrators
- **Last Updated:** November 29, 2024
- **Next Review:** After Architecture Phase

---

## 🎯 Executive Summary

**MedScribe AI** is a medical scribe application that automatically converts doctor-patient conversations in Tamil and Telugu into structured SOAP medical notes, reducing documentation time by 80% for Indian doctors in small clinics.

**Key Metrics:**
- Target: 50+ doctors in first 3 months
- Pricing: ₹500/month per doctor
- Languages: Tamil & Telugu (MVP), Hindi (Phase 2)
- Launch: 12 weeks from start

---

## 🎯 Product Overview

### Problem Statement

Indian doctors in small clinics spend 40-60% of consultation time writing notes instead of focusing on patients, leading to burnout, reduced patient time, and errors. Existing solutions are expensive (₹20,000-40,000/month for human scribes) or don't support Tamil/Telugu natively.

### Solution

MedScribe AI records doctor-patient conversations, transcribes Tamil/Telugu speech to text using Reverie API, extracts medical entities, and generates structured SOAP notes automatically.

### Target Users

1. **Primary:** Doctors in small clinics (1-5 doctors) in Tamil/Telugu speaking regions
2. **Secondary:** Clinic administrators managing documentation

---

## 🎯 Product Goals & Success Metrics

### Business Goals

1. **User Acquisition:** 50+ doctors using in first 3 months
2. **Revenue:** ₹500/month per doctor
3. **Retention:** <5% monthly churn rate
4. **Satisfaction:** 4.5/5 rating

### User Goals

1. **Time Savings:** 80% reduction in note-taking time
2. **Accuracy:** 90%+ note accuracy (with editing)
3. **Ease of Use:** Simple, one-click recording
4. **Language Support:** Native Tamil/Telugu notes

### Technical Goals

1. **Transcription Accuracy:** 50-70% confidence (Reverie API)
2. **Transcription Speed:** <5 seconds per minute of audio
3. **System Uptime:** 99.5% availability
4. **API Response:** <500ms (p95)

---

## 📱 Features & Requirements

### MVP Features (Must Have)

#### Epic 1: Audio Recording & Upload

**Feature 1.1: Web Audio Recording**
- **Description:** One-click audio recording in web browser
- **User Story:** As a doctor, I want to record consultations with one click so I can focus on the patient
- **Acceptance Criteria:**
  - [ ] Record button visible and accessible
  - [ ] Recording starts on click
  - [ ] Visual indicator shows recording status
  - [ ] Stop recording button available
  - [ ] Recording duration displayed
  - [ ] Works on Chrome, Firefox, Safari (latest versions)
  - [ ] Supports MP3, WAV formats
  - [ ] Maximum recording length: 30 minutes

**Feature 1.2: Audio File Upload**
- **Description:** Upload pre-recorded audio files
- **User Story:** As a doctor, I want to upload recorded audio so I can process it later
- **Acceptance Criteria:**
  - [ ] File upload button available
  - [ ] Supports MP3, WAV formats
  - [ ] File size limit: 50MB
  - [ ] Upload progress indicator
  - [ ] Error handling for invalid formats

**Feature 1.3: Audio Playback**
- **Description:** Play recorded audio for verification
- **User Story:** As a doctor, I want to listen to recorded audio to verify it's correct
- **Acceptance Criteria:**
  - [ ] Play button for recorded audio
  - [ ] Pause/resume functionality
  - [ ] Audio waveform visualization
  - [ ] Time scrubber for navigation

---

#### Epic 2: Speech-to-Text Transcription

**Feature 2.1: Tamil Transcription**
- **Description:** Convert Tamil speech to text using Reverie API
- **User Story:** As a doctor speaking Tamil, I want my speech converted to text automatically
- **Acceptance Criteria:**
  - [ ] Language selector (Tamil/Telugu)
  - [ ] Tamil selected by default
  - [ ] Audio sent to Reverie API
  - [ ] Transcription returned within 5 seconds per minute of audio
  - [ ] Confidence score displayed (50-70% expected)
  - [ ] Transcript displayed in Tamil script
  - [ ] Error handling for API failures
  - [ ] Retry mechanism for failed requests

**Feature 2.2: Telugu Transcription**
- **Description:** Convert Telugu speech to text using Reverie API
- **User Story:** As a doctor speaking Telugu, I want my speech converted to text automatically
- **Acceptance Criteria:**
  - [ ] Telugu language option available
  - [ ] Audio sent to Reverie API with Telugu language code
  - [ ] Transcription returned in Telugu script
  - [ ] Same performance as Tamil transcription
  - [ ] Confidence score displayed

**Feature 2.3: Real-time Transcription Display**
- **Description:** Show transcription as it's being processed
- **User Story:** As a doctor, I want to see transcription progress so I know it's working
- **Acceptance Criteria:**
  - [ ] Loading indicator during transcription
  - [ ] Progress percentage displayed
  - [ ] Transcript appears as it's generated
  - [ ] Final transcript highlighted when complete

**Feature 2.4: Transcript Editing**
- **Description:** Edit transcribed text for accuracy
- **User Story:** As a doctor, I want to edit transcripts to fix errors
- **Acceptance Criteria:**
  - [ ] Editable text area for transcript
  - [ ] Save edited transcript
  - [ ] Undo/redo functionality
  - [ ] Character count displayed
  - [ ] Auto-save draft every 30 seconds

---

#### Epic 3: Medical Note Generation

**Feature 3.1: Hybrid LLM + NER SOAP Generation** (Enhanced Approach)
- **Description:** Generate SOAP notes using LLM (Groq) with Hugging Face NER validation for 90%+ accuracy
- **User Story:** As a doctor, I want SOAP notes generated automatically from transcripts with high accuracy
- **Acceptance Criteria:**
  - [ ] Use Groq LLM API (free tier available) for SOAP structure
  - [ ] Use Hugging Face NER (`AventIQ-AI/bert-medical-entity-extraction`) for entity extraction
  - [ ] Use `ai4bharat/indic-bert` for Tamil/Telugu medical terms (+15% recall)
  - [ ] Process Tamil/Telugu transcripts natively
  - [ ] Generate structured SOAP notes (Subjective, Objective, Assessment, Plan)
  - [ ] Include Tamil/Telugu terms in brackets
  - [ ] Accuracy: 90%+ auto-fill (vs 80% benchmark)
  - [ ] Cross-validate LLM output with NER entities
  - [ ] Fallback to rule-based if LLM fails
  - [ ] Cost: ₹0.20 per note (Groq) + Free (Hugging Face)
  - [ ] Generation time: <3 seconds (p95)

**Feature 3.2: SOAP Note Formatting** (Updated)
- **Description:** Format LLM-generated SOAP notes with proper structure
- **User Story:** As a doctor, I want well-formatted SOAP notes that are easy to read
- **Acceptance Criteria:**
  - [ ] Clean Markdown formatting
  - [ ] All SOAP sections present (Subjective, Objective, Assessment, Plan)
  - [ ] Tamil/Telugu terms preserved in brackets
  - [ ] Editable sections
  - [ ] Professional medical note appearance
  - [ ] Export to PDF option

**Feature 3.3: Note Preview**
- **Description:** Preview generated note before saving
- **User Story:** As a doctor, I want to preview notes before saving
- **Acceptance Criteria:**
  - [ ] Preview button available
  - [ ] Formatted note display
  - [ ] All SOAP sections visible
  - [ ] Edit option from preview

**Feature 3.4: Note Saving**
- **Description:** Save notes to database
- **User Story:** As a doctor, I want to save notes for future reference
- **Acceptance Criteria:**
  - [ ] Save button available
  - [ ] Notes stored in MongoDB
  - [ ] Timestamp added automatically
  - [ ] Success confirmation message
  - [ ] Error handling for save failures

---

#### Epic 4: User Interface & Experience

**Feature 4.1: Dashboard**
- **Description:** Main dashboard showing recent notes and quick actions
- **User Story:** As a doctor, I want a dashboard to see my recent notes and start new recordings
- **Acceptance Criteria:**
  - [ ] Recent notes list (last 10)
  - [ ] Quick record button
  - [ ] Search functionality
  - [ ] Filter by date
  - [ ] Responsive design (mobile-friendly)

**Feature 4.2: Note List View**
- **Description:** List all saved notes
- **User Story:** As a doctor, I want to see all my notes in one place
- **Acceptance Criteria:**
  - [ ] Paginated list of notes
  - [ ] Sort by date (newest first)
  - [ ] Search by patient name or keywords
  - [ ] Click to view/edit note
  - [ ] Delete note option

**Feature 4.3: Note Detail View**
- **Description:** View and edit individual notes
- **User Story:** As a doctor, I want to view and edit individual notes
- **Acceptance Criteria:**
  - [ ] Full note display
  - [ ] Edit button
  - [ ] Delete button
  - [ ] Print option
  - [ ] Export to PDF option

**Feature 4.4: Language Selection**
- **Description:** Select Tamil or Telugu for transcription
- **User Story:** As a doctor, I want to choose my language for transcription
- **Acceptance Criteria:**
  - [ ] Language selector dropdown
  - [ ] Tamil and Telugu options
  - [ ] Default to Tamil
  - [ ] Language persists in session
  - [ ] Clear language labels

---

#### Epic 5: Authentication & Security

**Feature 5.1: User Registration**
- **Description:** Doctors can create accounts
- **User Story:** As a doctor, I want to create an account to use MedScribe AI
- **Acceptance Criteria:**
  - [ ] Registration form (name, email, password, clinic name)
  - [ ] Email validation
  - [ ] Password strength requirements (min 8 chars)
  - [ ] Email verification
  - [ ] Success message after registration

**Feature 5.2: User Login**
- **Description:** Secure login for doctors
- **User Story:** As a doctor, I want to login securely to access my notes
- **Acceptance Criteria:**
  - [ ] Login form (email, password)
  - [ ] JWT token authentication
  - [ ] Remember me option
  - [ ] Forgot password link
  - [ ] Error messages for invalid credentials

**Feature 5.3: Data Encryption**
- **Description:** Encrypt sensitive data (DPDP compliance)
- **User Story:** As a doctor, I want my patient data encrypted for security
- **Acceptance Criteria:**
  - [ ] AES-256 encryption for data at rest
  - [ ] TLS 1.3 for data in transit
  - [ ] Encrypted database fields
  - [ ] Secure API endpoints

**Feature 5.4: Audit Logging**
- **Description:** Log all data access for compliance
- **User Story:** As a clinic administrator, I want audit logs for compliance
- **Acceptance Criteria:**
  - [ ] Log all note access
  - [ ] Log all note edits
  - [ ] Log all note deletions
  - [ ] Timestamp and user ID in logs
  - [ ] Log retention: 7 years (medical records)

---

### Phase 2 Features (Future)

#### Epic 6: Multi-Language Support (Hindi)
- Hindi transcription support
- Hindi medical entity extraction
- Hindi SOAP note generation

#### Epic 7: ABDM/FHIR Integration
- FHIR-compliant note format
- ABDM Health ID integration
- Patient record linking
- Integration with Indian health records

#### Epic 8: Advanced Features
- Voice Activity Detection (VAD)
- Template-based notes
- Offline mode
- Mobile app (iOS/Android)
- Real-time collaboration

---

## 🔧 Non-Functional Requirements

### Performance

1. **Transcription Speed:**
   - <5 seconds per minute of audio
   - 95th percentile: <10 seconds

2. **API Response Time:**
   - <500ms for non-transcription endpoints
   - <5 seconds for transcription endpoints

3. **Page Load Time:**
   - Initial load: <2 seconds
   - Subsequent loads: <1 second

4. **Concurrent Users:**
   - Support 100+ concurrent users
   - No degradation up to 200 users

### Scalability

1. **Database:**
   - Handle 10,000+ notes per doctor
   - Support 1,000+ doctors

2. **Storage:**
   - Audio files: 50MB per recording
   - Notes: <100KB per note
   - Total storage: Scalable to 1TB+

3. **API Rate Limits:**
   - 100 transcriptions per hour per user
   - Burst: 10 concurrent transcriptions

### Security

1. **Authentication:**
   - JWT tokens with 24-hour expiry
   - Refresh tokens with 7-day expiry
   - Password hashing (bcrypt)

2. **Data Protection:**
   - AES-256 encryption at rest
   - TLS 1.3 in transit
   - DPDP Act compliance
   - Data retention: 7 years

3. **Access Control:**
   - Role-based access (RBAC)
   - Doctors can only access their notes
   - Audit logging for all access

### Reliability

1. **Uptime:**
   - 99.5% availability
   - <4 hours downtime per month

2. **Error Handling:**
   - Graceful degradation
   - User-friendly error messages
   - Automatic retry for API failures

3. **Backup:**
   - Daily database backups
   - 30-day backup retention
   - Disaster recovery plan

### Usability

1. **Accessibility:**
   - WCAG 2.1 AA compliance
   - Keyboard navigation
   - Screen reader support

2. **Mobile Support:**
   - Responsive design
   - Works on tablets and phones
   - Touch-friendly interface

3. **Internationalization:**
   - Tamil and Telugu UI support
   - Right-to-left text support (if needed)
   - Date/time localization

---

## 🎯 User Stories (Prioritized)

### Must Have (MVP)

1. **US-001:** As a doctor, I want to record consultations so I can transcribe them later
   - Priority: P0 (Critical)
   - Epic: Audio Recording

2. **US-002:** As a doctor speaking Tamil, I want my speech transcribed to Tamil text automatically
   - Priority: P0 (Critical)
   - Epic: Transcription

3. **US-003:** As a doctor speaking Telugu, I want my speech transcribed to Telugu text automatically
   - Priority: P0 (Critical)
   - Epic: Transcription

4. **US-004:** As a doctor, I want SOAP notes generated automatically from transcripts
   - Priority: P0 (Critical)
   - Epic: Note Generation

5. **US-005:** As a doctor, I want to edit transcripts and notes before saving
   - Priority: P0 (Critical)
   - Epic: Note Editing

6. **US-006:** As a doctor, I want to save notes for future reference
   - Priority: P0 (Critical)
   - Epic: Note Saving

7. **US-007:** As a doctor, I want to login securely to access my notes
   - Priority: P0 (Critical)
   - Epic: Authentication

### Should Have (MVP+)

8. **US-008:** As a doctor, I want to search my notes by keywords
   - Priority: P1 (High)
   - Epic: Search

9. **US-009:** As a doctor, I want to see my recent notes on dashboard
   - Priority: P1 (High)
   - Epic: Dashboard

10. **US-010:** As a doctor, I want to export notes to PDF
    - Priority: P1 (High)
    - Epic: Export

### Nice to Have (Phase 2)

11. **US-011:** As a doctor, I want Hindi transcription support
    - Priority: P2 (Medium)
    - Epic: Multi-Language

12. **US-012:** As a doctor, I want to link notes to patient records
    - Priority: P2 (Medium)
    - Epic: Patient Linking

---

## 📊 Technical Requirements

### Technology Stack

1. **Frontend:**
   - React 18+ with TypeScript
   - Tailwind CSS for styling
   - Axios for API calls
   - React Router for navigation

2. **Backend:**
   - FastAPI (Python 3.11+)
   - Uvicorn server
   - SQLAlchemy ORM
   - Pydantic for validation

3. **Database:**
   - PostgreSQL (structured data)
   - MongoDB (flexible notes)

4. **External APIs:**
   - Reverie API (speech-to-text)
   - Hugging Face (medical NER)

5. **Deployment:**
   - Docker containers
   - Render.com or AWS
   - Nginx reverse proxy

### API Specifications

**Base URL:** `https://api.medscribe.ai/v1`

**Endpoints:**

1. **POST /auth/register**
   - Register new doctor
   - Request: {name, email, password, clinic_name}
   - Response: {user_id, token}

2. **POST /auth/login**
   - Login doctor
   - Request: {email, password}
   - Response: {token, refresh_token}

3. **POST /audio/upload**
   - Upload audio file
   - Request: multipart/form-data (audio file, language)
   - Response: {audio_id, status}

4. **POST /transcription/transcribe**
   - Transcribe audio
   - Request: {audio_id, language}
   - Response: {transcript, confidence, entities}

5. **POST /notes/generate**
   - Generate SOAP note
   - Request: {transcript, entities}
   - Response: {note_id, soap_note}

6. **GET /notes**
   - List all notes
   - Request: query params (page, limit, search)
   - Response: {notes[], total, page}

7. **GET /notes/{note_id}**
   - Get note details
   - Response: {note}

8. **PUT /notes/{note_id}**
   - Update note
   - Request: {soap_note}
   - Response: {note}

9. **DELETE /notes/{note_id}**
   - Delete note
   - Response: {success}

---

## 🚫 Out of Scope (MVP)

- Real-time collaboration
- AI-powered medical suggestions
- Integration with clinic management systems
- Advanced analytics dashboard
- Multi-doctor team features
- Hindi language support (Phase 2)
- ABDM/FHIR integration (Phase 2)
- Mobile native apps (Phase 2)
- Offline mode (Phase 2)

---

## 📅 Timeline & Milestones

### Sprint Breakdown

**Sprint 1 (Weeks 1-2): Foundation**
- Project setup
- Authentication system
- Database schema
- Basic UI

**Sprint 2 (Weeks 3-4): Audio Recording**
- Audio recording UI
- File upload
- Audio playback

**Sprint 3 (Weeks 5-7): Transcription + SOAP Generation**
- Week 5: Reverie API integration
- Week 6: Tamil/Telugu transcription
- Week 7: Groq LLM + Hugging Face NER hybrid integration
- Week 7: SOAP note generation (hybrid approach)

**Sprint 4 (Week 8): Polish & Testing** (Optimized: 1 week)
- SOAP note refinement (few-shot examples)
- Indic-BERT integration for better Tamil/Telugu support
- Note editing improvements
- End-to-end testing
- Performance optimization (<3s SOAP generation)

**Sprint 5 (Weeks 10-11): Polish & Security**
- Encryption implementation
- Audit logging
- Performance optimization
- UI/UX refinements

**Sprint 5 (Weeks 9-10): Pilot & Launch** (Optimized: 2 weeks)
- Week 9: Pilot testing with 5 Kavali doctors (50 sample consultations)
- Week 9: Accuracy testing (target: 90%+ WER <15%)
- Week 10: User feedback integration
- Week 10: Launch preparation
- Week 10: Production deployment

---

## ✅ Success Criteria

### MVP Launch Criteria

- [ ] Tamil transcription working (WER <20%, confidence >50%)
- [ ] Telugu transcription working (WER <20%, confidence >50%)
- [ ] SOAP note generation functional (hybrid LLM + NER)
- [ ] 90%+ auto-fill accuracy (tested on 50 samples)
- [ ] 5 doctors testing successfully (pilot phase)
- [ ] Medical term accuracy: 85%+ (100 common terms tested)
- [ ] SOAP generation time: <3 seconds (p95)
- [ ] Cost monitoring: Reverie capped at ₹5K/month
- [ ] Whisper fallback implemented (if Reverie exceeds budget)
- [ ] DPDP compliance implemented
- [ ] Deployed to production
- [ ] Documentation complete

### Post-Launch Criteria (3 months)

- [ ] 50+ doctors using
- [ ] 70%+ daily active users
- [ ] 4.5/5 satisfaction rating
- [ ] <5% monthly churn
- [ ] Hindi support added (Phase 2)

---

## 💰 Cost Estimates

### MVP Monthly Costs (100 doctors, 20 consultations each)

| Service | Cost per Note | Monthly Cost | Notes |
|---------|---------------|--------------|-------|
| **Reverie API** | ₹2.50-5.00 | ₹5,000 (capped) | 5-10 min consultations |
| **Groq LLM** | ₹0.20 | ₹400 | After free tier |
| **Hugging Face** | Free | ₹0 | Self-hosted |
| **Whisper (fallback)** | Free | ₹0 | If Reverie exceeds |
| **Total** | - | **₹5,400** | Affordable for MVP |

### Risk Mitigation

- **Reverie Cost Cap:** ₹5,000/month for MVP trial
- **Fallback:** Whisper (free, 85-90% accuracy for Tamil/Telugu)
- **Monitoring:** Daily usage alerts at 80% of budget

---

## 📚 References

- Product Brief: `product-brief-medical-scribe.md`
- Phase 1 Research: `domain-research-medical-scribe.md`
- Test Results: `phase1-test-results-summary.md`
- Competitive Analysis: `competitive-analysis-indian-medical-scribes.md`
- PRD Enhancements: `prd-enhancements.md`
- Technical SOAP Process: `technical-soap-generation-process-llm.md`

---

## ✅ Next Steps

1. **Architecture Design** - System architecture
2. **UX Design** - Wireframes and mockups
3. **Epic Breakdown** - Detailed story breakdown
4. **Sprint Planning** - Implementation plan

---

**Document Status:** ✅ Complete  
**Ready for Architecture:** ✅ Yes  
**Next Document:** Architecture Design

---

**Last Updated:** November 29, 2024  
**Version:** 1.0

