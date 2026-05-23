# 🤖 Feature 1: AI Health Chat (Sanjeevani Assistant)

## Overview

The core AI Health Chat is the central feature of the SANJEEVANII platform. It is a medical-grade conversational AI built on top of local LLMs via **Ollama**, powered by a **Retrieval-Augmented Generation (RAG)** pipeline that sources answers from a curated medical dataset.

Users can type or paste health queries in **English, Hindi, or Hinglish**, attach medical images, and receive structured, empathetic, expert-level responses in real time via **Server-Sent Events (SSE) streaming**.

---

## 📁 Key Files

| File | Role |
|------|------|
| [`src/pages/Chat.tsx`](../src/pages/Chat.tsx) | React frontend — chat UI, message streaming |
| [`src/components/PromptBox.tsx`](../src/components/PromptBox.tsx) | Input component with tool selector, file upload |
| [`src/components/Sidebar.tsx`](../src/components/Sidebar.tsx) | Chat history sidebar |
| [`backend/server.js`](../backend/server.js) | Express backend — `/chat` route, LLM integration |
| [`backend/rag.js`](../backend/rag.js) | Medical RAG context injector |

---

## 🧠 How It Works

### Step-by-Step Flow

```
User types query → PromptBox
       ↓
Optional: Image uploaded → Vision model (llava) analyzes image
       ↓
Optional: Web Search tool → DuckDuckGo search results injected
       ↓
Language detection → Hinglish / English / Hindi
       ↓
RAG lookup → medical_val.jsonl (50k+ medical Q&A entries)
       ↓
System prompt selected → Standard / Tool-specific mode
       ↓
Ollama LLM (gpt-oss:120b-cloud) → Streaming response
       ↓
SSE stream → Chat UI renders token by token
```

---

## 🧩 Features

### 1. Message Classification Engine
The system prompt classifies every message before responding:

| Type | Description | Response Style |
|------|-------------|----------------|
| **Type 1** | Greeting / small talk | Warm, conversational |
| **Type 2** | Meta questions ("what can you do?") | Brief, friendly |
| **Type 3** | Medical / health query | Full structured format |
| **Type 4** | Emergency (`chest pain`, `can't breathe`) | Immediate 🚨 alert |
| **Type 5** | Mental health / crisis | Compassionate, crisis helplines |
| **Type 6** | Ambiguous | Asks one clarifying question |

### 2. Structured Medical Responses (Type 3)
All medical queries return a consistent 6-section format:
1. 🩺 Understanding Your Concern
2. What This Could Mean
3. Possible Causes (table format)
4. Safe Home Care
5. 🚨 When to See a Doctor
6. Quick Summary

### 3. Medical Image Analysis
- User uploads an image in the chat
- Image is base64 encoded and sent to the **`llava`** vision model via Ollama
- Vision model returns a detailed description of visible medical features
- Description is prepended to the user's query for the main LLM

### 4. RAG (Retrieval-Augmented Generation)
- Medical dataset (`medical_val.jsonl`, 50k+ entries) is pre-loaded at startup
- Each query extracts the top 3 relevant context entries (10 in Deep Research mode)
- Context is injected into the system prompt as a primary knowledge source

### 5. Tool Modes
Users can select a specialized mode from the prompt box:

| Tool | Mode | Behavior |
|------|------|----------|
| 🌐 Web Search | `searchWeb` | Live DuckDuckGo results injected |
| 📋 Plan | `writeCode` | Weekly schedule + diet plan output |
| 🤔 Think Longer | `thinkLonger` | Step-by-step analytical reasoning |
| 🔬 Deep Research | `deepResearch` | 10x RAG + comprehensive medical analysis |

### 6. Hinglish Detection & Language Matching
```javascript
// Detects Hinglish via keyword patterns
const hinglishPatterns = [
  /\b(mujhe|aap|kya|hai|ho|ka|ki|ke)\b/i,
  /\b(batao|chahiye|hota|raha|gaya)\b/i,
  /\b(sar|bukhar|dard|ilaaj|dawai|bimari)\b/i,
];
```
The AI automatically mirrors the user's language in its response.

### 7. Streaming Response (SSE)
- Backend streams tokens using `text/event-stream`
- Frontend uses `ReadableStream` and `requestAnimationFrame` to batch UI updates
- Thinking blocks (`<think>...</think>`) are parsed and shown as collapsible "Thinking Process" sections

---

## 🛡️ Safety Rules
- **NEVER diagnoses** — explains possibilities only
- **NEVER prescribes** — directs to doctors
- **Emergency detection first** on every message
- **Crisis response** includes Indian helpline numbers:
  - iCall: `9152987821`
  - Vandrevala Foundation: `1860-2662-345`

---

## 🔌 API Endpoints

### `POST /chat`
**Request:**
```json
{
  "message": "I have a fever of 102°F for 2 days",
  "images": ["<base64_string>"],
  "history": [{ "role": "user", "content": "..." }],
  "selectedTool": "searchWeb"
}
```
**Response:** `text/event-stream` (SSE)
```
data: {"content": "I hear "}
data: {"content": "you. "}
data: [DONE]
```

---

## ⚙️ Configuration

```javascript
// backend/server.js
const ollama = new Ollama({ host: 'http://localhost:11434' });
const selectedModel = 'gpt-oss:120b-cloud';
const datasetPath = path.join(__dirname, '..', 'medical_val.jsonl');
```

**Prerequisites:**
- Ollama running at `localhost:11434`
- Models: `gpt-oss:120b-cloud`, `llava`
- `medical_val.jsonl` in project root

---

## 🚀 Running the Backend

```bash
cd backend
npm install
npm start   # Starts on port 5000
```

---

## 📊 Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React + TypeScript + Vite |
| Backend | Node.js + Express |
| LLM | Ollama (local) |
| Vision | llava (multimodal) |
| RAG Dataset | medical_val.jsonl (50k+ entries) |
| Web Search | duck-duck-scrape |
| Streaming | Server-Sent Events (SSE) |
| Markdown | react-markdown + remark-gfm |
