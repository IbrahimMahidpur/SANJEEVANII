# 📚 SANJEEVANII — Feature Documentation Index

> Comprehensive documentation for every feature implemented in the SANJEEVANII Healthcare AI Platform.

---

## 🌟 Platform Overview

**SANJEEVANII** is an AI-powered, multilingual healthcare platform built for India. It combines local LLMs, Google Cloud AI services, RAG, voice interfaces, and real-time disease surveillance into a unified healthcare assistant.

---

## 📖 Feature Documentation

| # | Feature | File | Description |
|---|---------|------|-------------|
| 1 | 🤖 AI Health Chat | [01_AI_HEALTH_CHAT.md](./01_AI_HEALTH_CHAT.md) | Core conversational AI with RAG, streaming, image analysis, and multi-mode tools |
| 2 | 🚨 Outbreak Alert System | [02_OUTBREAK_ALERT_SYSTEM.md](./02_OUTBREAK_ALERT_SYSTEM.md) | Real-time disease surveillance, sparklines, heatmap, auto-refresh |
| 3 | 💊 Prescription Analysis | [03_PRESCRIPTION_ANALYSIS.md](./03_PRESCRIPTION_ANALYSIS.md) | OCR + LLM prescription parsing into structured medicine data |
| 4 | 🧠 CBT Voice Therapy | [04_CBT_VOICE_THERAPY.md](./04_CBT_VOICE_THERAPY.md) | Multi-agent voice therapy with Google STT/TTS, FAISS RAG, session memory |
| 5 | 🏥 Pharmacy Support | [05_PHARMACY_SUPPORT.md](./05_PHARMACY_SUPPORT.md) | Geo-based pharmacy finder, medicine availability, doctor booking |
| 6 | 💬 Community Forum | [06_COMMUNITY_FORUM.md](./06_COMMUNITY_FORUM.md) | Animated health discussion platform with dark/light mode |
| 7 | 🎤 June Talking Avatar | [07_JUNE_TALKING_AVATAR.md](./07_JUNE_TALKING_AVATAR.md) | Lip-synced animated avatar voice assistant |
| 8 | 🏗️ Backend Architecture | [08_BACKEND_ARCHITECTURE.md](./08_BACKEND_ARCHITECTURE.md) | Multi-service architecture, RAG system, startup scripts |
| 9 | 🎨 Frontend UI System | [09_FRONTEND_UI_SYSTEM.md](./09_FRONTEND_UI_SYSTEM.md) | React + Vite UI, glassmorphism design, routing, markdown |

---

## 🚀 Quick Start

```bash
# Install frontend dependencies
npm install

# Start all services
START_EVERYTHING.bat          # Windows — starts all services

# Or manually:
cd backend && npm start        # Main backend (port 5000)
cd cbt-backend && python app.py # CBT backend (port 8002)
npm run dev                    # Frontend (port 5173)
```

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SANJEEVANII Platform                    │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  React UI    │  Main API    │  CBT API     │  OCR API      │
│  :5173       │  :5000       │  :8002       │  :5001        │
│              │  (Node.js)   │  (FastAPI)   │  (Flask)      │
└──────┬───────┴──────┬───────┴──────┬───────┴───────┬───────┘
       │              │              │               │
       │         ┌────▼────┐    ┌───▼────┐    ┌────▼────┐
       │         │  Ollama │    │ Google │    │  OCR    │
       │         │  :11434 │    │ Cloud  │    │ Engine  │
       │         │ LLM/llava│   │STT+TTS │    │         │
       │         └─────────┘    └────────┘    └─────────┘
       │
       │    ┌──────────────────────────────────┐
       └───►│         Feature Pages            │
            ├──────────────────────────────────┤
            │ /          → Home (Orb + Menu)   │
            │ /chat      → AI Health Chat      │
            │ /outbreak  → Outbreak Alerts     │
            │ /rx        → Prescription OCR    │
            │ /pharmacy  → Pharmacy Support    │
            │ /community → Community Forum     │
            └──────────────────────────────────┘
```

---

## 🔑 Key Technologies

| Category | Technology |
|----------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Framer Motion |
| **Backend** | Node.js/Express, FastAPI, Flask |
| **AI / LLM** | Ollama (`gpt-oss:120b-cloud`, `llama3.2`, `llava`) |
| **Voice** | Google Cloud STT + TTS Neural2 |
| **RAG** | FAISS, Sentence Transformers, medical_val.jsonl |
| **Database** | JSON flat files, FAISS vector index |
| **Language** | Hindi, English, Hinglish support |

---

## 📁 Project Structure

```
SANJEEVANII/
├── docs/                    ← 📚 THIS — Feature documentation
├── src/                     ← React frontend
│   ├── pages/               ← Feature pages
│   ├── components/          ← Reusable UI components
│   └── services/            ← API service layers
├── backend/                 ← Main Node.js backend
│   ├── server.js            ← Express entry point
│   ├── pharmacy-api.js      ← Pharmacy CRUD
│   ├── outbreak-api.js      ← Outbreak data
│   ├── forum-api.js         ← Community forum
│   └── rag.js               ← Medical RAG
├── cbt-backend/             ← Python CBT voice therapy
│   ├── app.py               ← FastAPI entry point
│   ├── agents/              ← CBT multi-agent system
│   ├── memory/              ← Session + user memory
│   ├── safety/              ← Crisis detection
│   └── rag/                 ← FAISS retriever
├── prescriptionAnalysis/    ← OCR microservice
├── pharmacy-system/         ← Pharmacy system module
├── talking_june/            ← Avatar voice assistant
└── *.bat                    ← Windows startup scripts
```
