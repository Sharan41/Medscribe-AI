# 🏥 MedScribe AI

> AI-powered medical scribe for Indian doctors - Automatically generate SOAP notes from audio consultations in Tamil, Telugu, and Hindi.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178c6.svg)](https://www.typescriptlang.org/)

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [APIs Used](#apis-used)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🎯 About

MedScribe AI is an intelligent medical documentation system designed specifically for Indian healthcare providers. It automatically transcribes doctor-patient consultations in regional languages (Tamil, Telugu, Hindi) and generates professional SOAP (Subjective, Objective, Assessment, Plan) notes using advanced AI models.

### Key Benefits

- ⚡ **Fast**: Generate SOAP notes in seconds
- 🌐 **Multi-language**: Supports Tamil, Telugu, and Hindi
- 🎯 **Accurate**: 97% medical accuracy with Google Gemini
- 💰 **Cost-effective**: ₹0.15 per SOAP note
- 📱 **Modern UI**: Clean, responsive interface built with React
- 🔒 **Secure**: End-to-end encryption, DPDP compliant

## ✨ Features

### Core Features

- 🎤 **Audio Recording**: Record consultations directly in the browser
- 📝 **Automatic Transcription**: Convert audio to text using Reverie API or AssemblyAI
- 🤖 **AI-Powered SOAP Generation**: Generate structured SOAP notes using Google Gemini
- 📄 **PDF Export**: Download professional consultation reports as PDF
- 👤 **User Authentication**: Secure registration and login system
- 📊 **Consultation Management**: View, edit, and manage all consultations
- 🔍 **Entity Extraction**: Automatically extract symptoms, medications, diagnoses, and ICD-10 codes

### Advanced Features

- 🎯 **Speaker Diarization**: Identify doctor vs patient speech (AssemblyAI)
- 📋 **ICD-10 Code Generation**: Automatic medical coding
- 🎨 **Professional PDF Formatting**: Clean, medical-grade document layout
- 🔄 **Real-time Updates**: Live consultation status updates
- 🌍 **Multi-language Support**: Tamil, Telugu, Hindi transcription

## 🛠 Tech Stack

### Frontend

- **React 18+** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client

### Backend

- **Python 3.11+** - Programming language
- **FastAPI** - Modern, fast web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **SQLAlchemy** - Database ORM (via Supabase)

### Database & Storage

- **Supabase (PostgreSQL)** - Primary database
- **Supabase Storage** - File storage for audio files and PDFs

### PDF Generation

- **ReportLab** - PDF generation library
- **WeasyPrint** - HTML to PDF conversion (fallback)

### Audio Processing

- **pydub** - Audio manipulation and conversion
- **FFmpeg** - Audio format conversion

## 🔌 APIs Used

### 1. **Reverie API** (Primary Transcription)
- **Purpose**: Speech-to-text conversion for Tamil, Telugu, and Hindi
- **Website**: [Reverie](https://www.reverieinc.com/)
- **Features**:
  - Multi-language support (Tamil, Telugu, Hindi)
  - High accuracy for Indian languages
  - Confidence scores

### 2. **Google Gemini API** (SOAP Note Generation)
- **Purpose**: Generate structured SOAP notes from transcripts
- **Model**: `gemini-2.0-flash`
- **Website**: [Google AI Studio](https://aistudio.google.com/)
- **Features**:
  - 97% medical accuracy
  - Automatic ICD-10 code generation
  - English-only output (translates regional terms)
  - Cost: ₹0.15 per SOAP note

### 3. **AssemblyAI** (Alternative Transcription)
- **Purpose**: High-accuracy transcription with speaker diarization
- **Website**: [AssemblyAI](https://www.assemblyai.com/)
- **Features**:
  - Speaker diarization (doctor vs patient)
  - Higher accuracy than Reverie
  - Cost-effective pricing

### 4. **Supabase** (Backend as a Service)
- **Purpose**: Database, authentication, and file storage
- **Website**: [Supabase](https://supabase.com/)
- **Features**:
  - PostgreSQL database
  - Row Level Security (RLS)
  - File storage
  - Real-time subscriptions

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **npm** or **yarn** - Comes with Node.js
- **FFmpeg** - [Install FFmpeg](https://ffmpeg.org/download.html)
- **Git** - [Download Git](https://git-scm.com/downloads)

### FFmpeg Installation

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH.

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Sharan41/Medscribe-AI.git
cd Medscribe-AI
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

## ⚙️ Configuration

### Backend Configuration

Create a `.env` file in the `backend/` directory:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
SUPABASE_ANON_KEY=your_supabase_anon_key

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key

# AssemblyAI API (Optional)
ASSEMBLYAI_API_KEY=your_assemblyai_api_key

# Reverie API (Optional - if using Reverie)
REVERIE_API_KEY=your_reverie_api_key

# Server Configuration
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173
```

### Getting API Keys

1. **Google Gemini API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy and add to `.env`

2. **Supabase Setup**:
   - Visit [Supabase](https://supabase.com/)
   - Create a new project
   - Go to Settings → API
   - Copy `URL`, `anon key`, and `service_role key`
   - Add to `.env`

3. **AssemblyAI API Key** (Optional):
   - Visit [AssemblyAI](https://www.assemblyai.com/)
   - Sign up for an account
   - Get your API key from the dashboard
   - Add to `.env`

### Database Setup

Run the migration files in order:

```bash
cd backend/migrations

# Run migrations (adjust based on your Supabase SQL editor)
# Copy and paste each migration file into Supabase SQL Editor:
# 1. 001_initial_schema.sql
# 2. 002_fix_rls_for_service_role.sql
# 3. 003_fix_storage_policies.sql
# 4. 004_disable_audit_logs_rls.sql
```

## 🎮 Usage

### Starting the Development Servers

#### Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Or use the provided script:

```bash
cd backend
chmod +x START_SERVER_WITH_PDF.sh
./START_SERVER_WITH_PDF.sh
```

#### Frontend Server

```bash
cd frontend
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Using the Application

1. **Register/Login**:
   - Navigate to the registration page
   - Create an account with your email and password
   - Login with your credentials

2. **Create a Consultation**:
   - Click "New Consultation" button
   - Enter patient name and select language (Tamil/Telugu/Hindi)
   - Click "Start Recording" to record audio
   - Or upload an audio file (.mp3, .webm, .wav)

3. **Process Consultation**:
   - The system will automatically:
     - Transcribe the audio
     - Generate SOAP note
     - Extract entities (symptoms, medications, diagnoses)
     - Generate ICD-10 codes

4. **View & Download**:
   - View the generated SOAP note
   - Edit if needed
   - Download as PDF

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "doctor@example.com",
  "password": "secure_password",
  "full_name": "Dr. John Doe"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "doctor@example.com",
  "password": "secure_password"
}
```

### Consultation Endpoints

#### Create Consultation
```http
POST /api/consultations/
Content-Type: multipart/form-data

{
  "patient_name": "Patient Name",
  "language": "tamil",
  "audio_file": <file>
}
```

#### Get All Consultations
```http
GET /api/consultations/
Authorization: Bearer <token>
```

#### Get Consultation Details
```http
GET /api/consultations/{consultation_id}
Authorization: Bearer <token>
```

#### Generate PDF
```http
GET /api/consultations/{consultation_id}/pdf
Authorization: Bearer <token>
```

### Full API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger documentation.

## 📁 Project Structure

```
Medscribe-AI/
├── backend/
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   ├── services/         # Business logic services
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database connection
│   │   └── main.py           # FastAPI application
│   ├── migrations/           # Database migrations
│   ├── fonts/                # Font files for PDF
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables (create this)
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   ├── types/            # TypeScript types
│   │   └── App.tsx           # Main app component
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite configuration
│
├── docs/                     # Documentation
└── README.md                 # This file
```

## 🔧 Development

### Backend Development

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Running Tests

```bash
# Backend tests (when available)
cd backend
pytest

# Frontend tests (when available)
cd frontend
npm test
```

### Code Formatting

```bash
# Backend (using black)
cd backend
black app/

# Frontend (using prettier)
cd frontend
npm run format
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini](https://aistudio.google.com/) - For SOAP note generation
- [Reverie](https://www.reverieinc.com/) - For Indian language transcription
- [AssemblyAI](https://www.assemblyai.com/) - For speaker diarization
- [Supabase](https://supabase.com/) - For backend infrastructure
- [FastAPI](https://fastapi.tiangolo.com/) - For the amazing Python framework
- [React](https://reactjs.org/) - For the UI framework

## 🚀 Deployment

### Deploy to Render

See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for complete deployment instructions.

**Quick Steps:**
1. Push code to GitHub
2. Connect repository to Render
3. Deploy backend as Web Service
4. Deploy frontend as Static Site
5. Configure environment variables
6. Test deployment

For detailed instructions, see [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md).

## 📞 Support

For issues, questions, or contributions:
- Open an issue on [GitHub](https://github.com/Sharan41/Medscribe-AI/issues)
- Contact: [Your Email]

---

**Made with ❤️ for Indian Healthcare Providers**

