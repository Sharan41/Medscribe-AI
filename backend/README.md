# MedScribe AI Backend

FastAPI backend for MedScribe AI - Medical Transcription Assistant

## Setup

### 1. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### 4. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Supabase client
│   ├── api/                 # API endpoints
│   ├── models/             # Pydantic models
│   ├── services/            # Business logic
│   └── utils/               # Utilities
├── tests/                   # Tests
├── requirements.txt         # Dependencies
└── .env.example            # Environment template
```

## API Endpoints

- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger)
- `GET /redoc` - API documentation (ReDoc)

## Development

### Run Tests

```bash
pytest
```

### Format Code

```bash
black app/
```

### Lint Code

```bash
flake8 app/
```

