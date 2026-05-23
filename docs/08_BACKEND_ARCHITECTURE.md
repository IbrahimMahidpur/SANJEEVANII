# 🏗️ Feature 8: Backend Architecture & RAG System

## Overview

The SANJEEVANII backend is a multi-service architecture with three independent backend services running in parallel, each serving a different domain. At its core is a **Retrieval-Augmented Generation (RAG)** pipeline that enriches AI responses with curated medical knowledge.

---

## 📁 Services Overview

| Service | Port | Technology | Purpose |
|---------|------|-----------|---------|
| Main Backend | 5000 | Node.js + Express | Chat, pharmacy, forum, outbreak APIs |
| CBT Backend | 8002 | FastAPI + Python | Voice therapy pipeline |
| OCR Service | 5001 | Flask + Python | Prescription image OCR |
| Frontend | 5173 | Vite + React | UI serving |

---

## 🧩 Main Backend (Node.js - Port 5000)

### Architecture
```
backend/server.js  →  Entry point
├── /chat               → AI chat + RAG + streaming
├── /api/pharmacy       → pharmacyAPI (pharmacy-api.js)
├── /api/medicine       → medicineAPI (medicine-api.js)
├── /api/outbreak       → outbreakAPI (outbreak-api.js)
├── /api/pharmacy-support → pharmacySupportRouter
├── /api/places         → placesAPIRouter (Google Places)
├── /api/forum          → forumAPI (forum-api.js)
└── /api/prescription/refine → LLM prescription parser
```

### Medical RAG System (`backend/rag.js`)

The RAG system loads a large medical Q&A dataset and enables semantic context retrieval:

```javascript
// Load at startup
medicalRAG.loadDataset(datasetPath);  // medical_val.jsonl (50k+ entries)

// Per-query context retrieval
const ragContext = medicalRAG.getContext(userMessage, 3);  // Top 3 results
// Deep research mode gets 10 results
const ragContext = medicalRAG.getContext(userMessage, 10);
```

The retrieved context is injected into the system prompt as the **primary knowledge source**, with the LLM instructed to prioritize it over its parametric knowledge.

### Environment Variables (`backend/.env`)
```env
GOOGLE_MAPS_API_KEY=...
# Other API keys
```

### Key NPM Dependencies
```json
{
  "ollama": "^0.x",
  "duck-duck-scrape": "^2.x",
  "express": "^4.x",
  "cors": "^2.x",
  "dotenv": "^16.x"
}
```

---

## 🐍 CBT Backend (FastAPI - Port 8002)

### Module Loading at Startup
```python
# All modules loaded at startup with graceful degradation
RAG_AVAILABLE    # FAISS retriever (195k chunks)
MEMORY_AVAILABLE # Session + long-term user memory
SAFETY_AVAILABLE # Crisis detection
AGENTS_AVAILABLE # CBT multi-agent pipeline
```

### Key Python Dependencies (`cbt-backend/requirements.txt`)
```
fastapi
uvicorn
google-cloud-speech
google-cloud-texttospeech
aiofiles
faiss-cpu
sentence-transformers
langchain
```

---

## 🌐 Real-Time APIs (`backend/realtime-apis.js`)

Integration with free public health APIs for live data augmentation.

---

## 🔧 Startup Scripts

| Script | Purpose |
|--------|---------|
| `RUN_PROJECT.bat` | Full project startup |
| `START_EVERYTHING.bat` | All services including June VA |
| `START_ALL_MODULES.bat` | All backend modules |
| `RESTART_SANJEEVANI.bat` | Restart all services |
| `start_sanjeevani_backend.bat` | Backend only |
| `run_cbt_backend.bat` | CBT service only |
| `start_frontend.bat` | Frontend only |

---

## 📊 Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite |
| Main API | Node.js 18+ + Express 4 |
| CBT API | Python 3.11 + FastAPI |
| OCR API | Python + Flask |
| LLM (local) | Ollama (`gpt-oss:120b-cloud`, `llama3.2`, `llava`) |
| STT/TTS | Google Cloud APIs |
| Vector DB | FAISS |
| RAG Dataset | medical_val.jsonl (50k+ Q&A pairs) |

---

## 🚀 Full Stack Startup

```bash
# Terminal 1 — Main Backend
cd backend && npm start

# Terminal 2 — CBT Backend
cd cbt-backend && python app.py

# Terminal 3 — OCR Service
cd prescriptionAnalysis/MediScribe-OCR && python app.py

# Terminal 4 — Frontend
npm run dev

# Or use the all-in-one script:
START_EVERYTHING.bat
```
