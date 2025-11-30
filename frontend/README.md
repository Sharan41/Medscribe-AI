# MedScribe AI - Frontend

React + TypeScript + Tailwind CSS frontend for Medical Scribe application.

## 🚀 Quick Start

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm run dev
```

Server will run on: http://localhost:3000

### Build for Production

```bash
npm run build
```

## 📁 Project Structure

```
src/
├── components/     # Reusable components
├── pages/         # Page components
├── services/      # API services
├── context/       # React context providers
├── App.tsx        # Main app component
└── main.tsx       # Entry point
```

## 🔧 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client

## 🌐 API Configuration

Backend API runs on: http://localhost:8000

Proxy configured in `vite.config.ts` to forward `/api/*` requests to backend.

