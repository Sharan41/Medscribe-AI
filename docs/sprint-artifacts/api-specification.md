# API Specification: MedScribe AI

**Document Type:** API Design Specification  
**Project:** MedScribe AI  
**Version:** 1.0  
**Date:** November 29, 2024  
**Base URL:** `https://api.medscribe.ai/v1`

---

## 📋 API Overview

### Authentication
- **Method:** Supabase Auth (JWT Bearer Token)
- **Header:** `Authorization: Bearer <token>`
- **Token Expiry:** 24 hours
- **Refresh Token:** 7 days
- **MFA:** Required for healthcare compliance (ONC standard)

### Response Format
- **Content-Type:** `application/json`
- **Encoding:** UTF-8
- **Date Format:** ISO 8601

### Healthcare Headers (HIPAA/FHIR Standard)
```
X-Request-ID: uuid          # Traceability
X-Clinic-ID: uuid           # Multi-clinic support
X-Compliance: DPDP-2023     # Audit trail
X-API-Cost: 0.75            # ₹0.50 Reverie + ₹0.25 Groq
X-Estimated-Time: 45        # seconds remaining
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'none'
```

### Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

---

## 🔐 Authentication Endpoints

### POST /auth/register

**Description:** Register a new doctor account

**Request:**
```json
{
  "name": "Dr. Priya",
  "email": "priya@clinic.com",
  "password": "SecurePassword123!",
  "clinic_name": "Priya Clinic"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "priya@clinic.com",
    "name": "Dr. Priya",
    "clinic_name": "Priya Clinic"
  },
  "message": "Registration successful. Please verify your email."
}
```

**Errors:**
- `400`: Validation error (email format, password strength)
- `409`: Email already exists

---

### POST /auth/login

**Description:** Login and get JWT token

**Request:**
```json
{
  "email": "priya@clinic.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "refresh_token_string",
  "user": {
    "id": "uuid",
    "email": "priya@clinic.com",
    "name": "Dr. Priya",
    "mfa_enabled": true,
    "mfa_required": true
  },
  "expires_in": 86400,
  "mfa_required": true
}
```

**Errors:**
- `401`: Invalid credentials
- `403`: Account inactive
- `428`: MFA required (if MFA enabled)

**Note:** If MFA is enabled, returns `mfa_required: true`. User must complete MFA verification.

---

### POST /auth/mfa/setup

**Description:** Set up Multi-Factor Authentication (Required for healthcare compliance)

**Request:**
```json
{
  "method": "totp"  // Time-based One-Time Password
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "qr_code": "data:image/png;base64,...",
  "secret": "JBSWY3DPEHPK3PXP",
  "backup_codes": ["12345678", "87654321", ...],
  "message": "Scan QR code with authenticator app"
}
```

---

### POST /auth/mfa/verify

**Description:** Verify MFA code during login

**Request:**
```json
{
  "mfa_token": "token_from_login_response",
  "mfa_code": "123456"  // 6-digit code from authenticator app
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "token": "final_jwt_token",
  "user": {...},
  "expires_in": 86400
}
```

**Errors:**
- `401`: Invalid MFA code
- `403`: MFA code expired

---

### POST /auth/refresh

**Description:** Refresh access token

**Request:**
```json
{
  "refresh_token": "refresh_token_string"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "token": "new_jwt_token",
  "expires_in": 86400
}
```

---

## 🏥 Unified Consultation Endpoint (Optimized)

### POST /consultations

**Description:** Upload audio and start complete processing pipeline (transcription + SOAP generation)

**Request:** `multipart/form-data`
```
file: <audio_file> (MP3/WAV, max 50MB)
language: "ta" | "te"
patient_name: "Patient Name" (optional)
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "consultation_id": "uuid",
  "status": "processing",
  "websocket_url": "wss://api.medscribe.ai/ws/{consultation_id}",
  "poll_url": "/consultations/{consultation_id}",
  "estimated_time": 45,
  "message": "Consultation processing started"
}
```

**Headers:**
```
X-Request-ID: uuid
X-API-Cost: 0.75
X-Estimated-Time: 45
```

**Errors:**
- `400`: Invalid file format or size
- `413`: File too large (>50MB)
- `429`: Rate limit exceeded

**Note:** This endpoint combines audio upload + transcription + SOAP generation into one async flow.

---

### GET /consultations/{consultation_id}

**Description:** Get consultation status and results (single source of truth for polling)

**Response (200 OK) - Processing:**
```json
{
  "id": "uuid",
  "status": "processing",
  "progress": {
    "transcription": "completed",
    "entity_extraction": "processing",
    "soap_generation": "pending"
  },
  "estimated_time_remaining": 30,
  "created_at": "2024-11-29T10:00:00Z"
}
```

**Response (200 OK) - Completed:**
```json
{
  "id": "uuid",
  "status": "completed",
  "patient_name": "Patient Name",
  "language": "ta",
  "transcript": {
    "text": "நோயாளிக்கு காய்ச்சல் உள்ளது...",
    "confidence": 0.65,
    "transcription_method": "reverie"
  },
  "entities": [
    {
      "word": "காய்ச்சல்",
      "type": "SYMPTOM",
      "confidence": 0.95
    }
  ],
  "soap_note": {
    "subjective": ["Fever [காய்ச்சல்]", "Headache [தலைவலி]"],
    "objective": ["BP: 120/80 mmHg", "Temperature: 101°F"],
    "assessment": ["Viral fever"],
    "plan": [
      {
        "medication": "Paracetamol [பாராசிட்டமால்]",
        "dosage": "500mg",
        "frequency": "3 times daily"
      }
    ],
    "formatted": "# Medical Consultation Note\n\n## Subjective\n..."
  },
  "pdf_url": "https://storage.medscribe.ai/notes/{uuid}.pdf",
  "fhir_bundle": {
    "resourceType": "Bundle",
    "entry": [...]
  },
  "icd_codes": ["R50.9", "G44.1"],
  "generation_method": "hybrid",
  "generation_time": 2.5,
  "cost": 0.75,
  "created_at": "2024-11-29T10:00:00Z",
  "completed_at": "2024-11-29T10:00:45Z"
}
```

**Status Values:**
- `processing`: In progress
- `completed`: Success
- `failed`: Error occurred

**Polling Pattern:** Frontend polls every 2 seconds until status is "completed" or "failed"

---

### WebSocket: wss://api.medscribe.ai/ws/{consultation_id}

**Description:** Real-time updates for consultation processing

**Connection:**
```javascript
const ws = new WebSocket(`wss://api.medscribe.ai/ws/${consultation_id}`);

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // update.status, update.progress, etc.
};
```

**Message Format:**
```json
{
  "type": "progress" | "completed" | "error",
  "consultation_id": "uuid",
  "status": "processing",
  "progress": {
    "transcription": "completed",
    "soap_generation": "processing"
  },
  "data": {...}  // Full consultation data when completed
}
```

---

## 📋 Notes Endpoints (Optimized)

### GET /notes

**Description:** List all notes for authenticated user

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `search`: Search query (patient name, keywords)
- `language`: Filter by language ("ta" | "te")
- `sort`: Sort order ("created_at" | "updated_at", default: "created_at")
- `order`: "asc" | "desc" (default: "desc")

**Response (200 OK):**
```json
{
  "success": true,
  "notes": [
    {
      "id": "uuid",
      "consultation_id": "uuid",
      "patient_name": "Patient Name",
      "title": "Consultation - 2024-11-29",
      "language": "ta",
      "status": "completed",
      "created_at": "2024-11-29T10:10:00Z",
      "updated_at": "2024-11-29T10:15:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

---

### GET /notes/{note_id}

**Description:** Get note details

**Response (200 OK):**
```json
{
  "success": true,
  "note": {
    "id": "uuid",
    "consultation_id": "uuid",
    "patient_name": "Patient Name",
    "language": "ta",
    "transcript": {
      "text": "நோயாளிக்கு காய்ச்சல் உள்ளது...",
      "confidence": 0.65
    },
    "soap_note": {
      "subjective": [...],
      "objective": [...],
      "assessment": [...],
      "plan": [...],
      "formatted": "markdown string"
    },
    "entities": [...],
    "icd_codes": ["R50.9"],
    "pdf_url": "https://storage.medscribe.ai/notes/{uuid}.pdf",
    "created_at": "2024-11-29T10:10:00Z",
    "updated_at": "2024-11-29T10:15:00Z",
    "version": 2
  }
}
```

---

### GET /notes/{note_id}/pdf

**Description:** Download professional PDF of SOAP note

**Response (200 OK):**
- **Content-Type:** `application/pdf`
- **Headers:**
  ```
  Content-Disposition: attachment; filename="consult-{uuid}.pdf"
  Content-Type: application/pdf
  ```
- **Body:** PDF file bytes

**Features:**
- Professional medical note template
- Clinic letterhead (if configured)
- Doctor signature line
- Tamper-proof formatting

---

### POST /notes/{note_id}/fhir

**Description:** Export note as FHIR Bundle (ABDM compatible)

**Response (200 OK):**
```json
{
  "success": true,
  "fhir_bundle": {
    "resourceType": "Bundle",
    "type": "document",
    "entry": [
      {
        "resource": {
          "resourceType": "Observation",
          "code": {
            "coding": [{
              "system": "http://loinc.org",
              "code": "8480-6",
              "display": "Systolic blood pressure"
            }],
            "valueQuantity": {
              "value": 120,
              "unit": "mmHg"
            }
          }
        }
      },
      {
        "resource": {
          "resourceType": "Condition",
          "code": {
            "coding": [{
              "system": "http://hl7.org/fhir/sid/icd-10",
              "code": "R50.9",
              "display": "Fever, unspecified"
            }]
          }
        }
      },
      {
        "resource": {
          "resourceType": "MedicationRequest",
          "medicationCodeableConcept": {
            "coding": [{
              "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
              "code": "161",
              "display": "Paracetamol"
            }]
          },
          "dosageInstruction": [{
            "doseQuantity": {
              "value": 500,
              "unit": "mg"
            },
            "frequency": "3 times daily"
          }]
        }
      }
    ]
  },
  "abdm_compatible": true
}
```

**Use Case:** Export for ABDM sandbox integration (Phase 2)

---

### PUT /notes/{note_id}

**Description:** Update SOAP note

**Request:**
```json
{
  "soap_note": {
    "subjective": ["Updated symptoms..."],
    "objective": ["Updated findings..."],
    "assessment": ["Updated diagnosis..."],
    "plan": ["Updated plan..."]
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "note": {
    "id": "uuid",
    "updated_at": "2024-11-29T10:20:00Z",
    "version": 3
  },
  "message": "Note updated successfully"
}
```

---

### DELETE /notes/{note_id}

**Description:** Delete note (soft delete)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Note deleted successfully"
}
```

**Note:** Creates audit log entry, soft deletes (can be restored)

---

### GET /notes

**Description:** List all notes for authenticated user

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `search`: Search query (patient name, keywords)
- `language`: Filter by language ("ta" | "te")
- `sort`: Sort order ("created_at" | "updated_at", default: "created_at")
- `order`: "asc" | "desc" (default: "desc")

**Response (200 OK):**
```json
{
  "success": true,
  "notes": [
    {
      "id": "uuid",
      "consultation_id": "uuid",
      "patient_name": "Patient Name",
      "title": "Consultation - 2024-11-29",
      "language": "ta",
      "created_at": "2024-11-29T10:10:00Z",
      "updated_at": "2024-11-29T10:15:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

---

### GET /notes/{note_id}

**Description:** Get note details

**Response (200 OK):**
```json
{
  "success": true,
  "note": {
    "id": "uuid",
    "consultation_id": "uuid",
    "patient_name": "Patient Name",
    "language": "ta",
    "transcript": {
      "text": "நோயாளிக்கு காய்ச்சல் உள்ளது...",
      "confidence": 0.65
    },
    "soap_note": {
      "subjective": [...],
      "objective": [...],
      "assessment": [...],
      "plan": [...],
      "formatted": "markdown string"
    },
    "entities": [...],
    "created_at": "2024-11-29T10:10:00Z",
    "updated_at": "2024-11-29T10:15:00Z",
    "version": 2
  }
}
```

**Errors:**
- `404`: Note not found
- `403`: Not authorized (not user's note)

---

### PUT /notes/{note_id}

**Description:** Update SOAP note

**Request:**
```json
{
  "soap_note": {
    "subjective": ["Updated symptoms..."],
    "objective": ["Updated findings..."],
    "assessment": ["Updated diagnosis..."],
    "plan": ["Updated plan..."]
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "note": {
    "id": "uuid",
    "updated_at": "2024-11-29T10:20:00Z",
    "version": 3
  },
  "message": "Note updated successfully"
}
```

---

### DELETE /notes/{note_id}

**Description:** Delete note (soft delete)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Note deleted successfully"
}
```

**Note:** Creates audit log entry, soft deletes (can be restored)

---

## 👤 User Endpoints

### GET /users/me

**Description:** Get current user profile

**Response (200 OK):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "priya@clinic.com",
    "name": "Dr. Priya",
    "clinic_name": "Priya Clinic",
    "created_at": "2024-11-29T08:00:00Z"
  }
}
```

---

### PUT /users/me

**Description:** Update user profile

**Request:**
```json
{
  "name": "Dr. Priya Updated",
  "clinic_name": "Updated Clinic Name"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "name": "Dr. Priya Updated",
    "clinic_name": "Updated Clinic Name",
    "updated_at": "2024-11-29T11:00:00Z"
  }
}
```

---

### PUT /users/me/clinic

**Description:** Update clinic profile (DPDP compliance)

**Request:**
```json
{
  "clinic_name": "Kavali Clinic",
  "address": "123 Main Rd, Kavali, Andhra Pradesh",
  "license_no": "AP-MC-45678",
  "doctor_reg": "AP-12345",
  "phone": "+91-9876543210",
  "email": "clinic@kavali.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "clinic": {
    "id": "uuid",
    "clinic_name": "Kavali Clinic",
    "address": "123 Main Rd, Kavali, Andhra Pradesh",
    "license_no": "AP-MC-45678",
    "doctor_reg": "AP-12345",
    "updated_at": "2024-11-29T11:00:00Z"
  }
}
```

---

### GET /audit/logs

**Description:** Get audit logs for authenticated user (DPDP compliance)

**Query Parameters:**
- `from_date`: Start date (ISO 8601)
- `to_date`: End date (ISO 8601)
- `action`: Filter by action ("create", "read", "update", "delete")
- `resource_type`: Filter by resource type ("note", "consultation")
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50, max: 200)

**Response (200 OK):**
```json
{
  "success": true,
  "logs": [
    {
      "id": "uuid",
      "action": "create",
      "resource_type": "note",
      "resource_id": "uuid",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2024-11-29T10:10:00Z",
      "details": {}
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 125,
    "pages": 3
  }
}
```

**Note:** Users can only view their own audit logs (enforced by Row Level Security)

---

## 📊 Health & Status Endpoints

### GET /health

**Description:** Health check endpoint

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-29T10:00:00Z",
  "services": {
    "database": "connected",
    "reverie_api": "available",
    "groq_api": "available",
    "huggingface": "available"
  }
}
```

---

### GET /status

**Description:** System status and metrics

**Response (200 OK):**
```json
{
  "status": "operational",
  "uptime": 99.5,
  "metrics": {
    "total_notes": 1250,
    "total_consultations": 1500,
    "avg_transcription_time": 4.2,
    "avg_soap_generation_time": 2.5
  }
}
```

---

## 🔒 Rate Limiting (Healthcare Realistic)

### Limits by Tier

**Free Tier:**
- Consultations: 10/hour
- General API: 100/hour
- Burst: 2 concurrent

**Paid Tier (₹500/month):**
- Consultations: 100/hour
- General API: 1000/hour
- Burst: 5 concurrent

**Enterprise Tier:**
- Consultations: 1000/hour
- General API: 10000/hour
- Burst: 20 concurrent

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1638201600
X-API-Cost: 0.75
X-Estimated-Time: 45
```

---

## 📝 Request/Response Models

### Pydantic Models (Python)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    clinic_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AudioUpload(BaseModel):
    language: str  # "ta" | "te"
    patient_name: Optional[str] = None

class TranscriptionRequest(BaseModel):
    consultation_id: str
    language: str  # "ta" | "te"

class SOAPGenerationRequest(BaseModel):
    consultation_id: str
    transcript: str
    language: str  # "ta" | "te"
    patient_name: Optional[str] = None

class SOAPNote(BaseModel):
    subjective: List[str]
    objective: List[str]
    assessment: List[str]
    plan: List[dict]
    formatted: str
```

---

## 🚨 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Invalid or missing token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | External service down |

---

## 📚 OpenAPI Specification

**Location:** `/docs` (Swagger UI)  
**Format:** OpenAPI 3.0  
**Interactive:** Yes (try endpoints directly)

---

## ✅ Next Steps

1. **Database Schema** - Complete schema design
2. **Security Architecture** - Detailed security plan
3. **Integration Design** - External API integration specs
4. **Implementation** - Start coding!

---

**Document Status:** ✅ Complete  
**Ready for:** Database Schema Design  
**Next Document:** `database-schema.md`

---

**Last Updated:** November 29, 2024  
**Version:** 1.0

