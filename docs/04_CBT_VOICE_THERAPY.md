# 🧠 Feature 4: CBT Voice Therapy (June VA)

## Overview

The **CBT (Cognitive Behavioral Therapy) Voice Therapy** module is a sophisticated AI-powered mental health companion called **June**. It provides real-time, empathetic voice-based therapy sessions using a full **Speech-to-Text → Multi-Agent CBT Analysis → Text-to-Speech** pipeline.

The system supports **Hinglish** (Hindi + English mixed speech), uses **Google Cloud STT/TTS Neural2** voices, integrates a **FAISS-based RAG knowledge base** of CBT techniques, and maintains **session and long-term user memory** across conversations.

---

## 📁 Key Files

| File | Role |
|------|------|
| [`cbt-backend/app.py`](../cbt-backend/app.py) | FastAPI main server — full voice session pipeline |
| [`cbt-backend/agents/analyzer.py`](../cbt-backend/agents/analyzer.py) | Agent 1: Emotion & distortion analyzer |
| [`cbt-backend/agents/evidence_agent.py`](../cbt-backend/agents/evidence_agent.py) | Agent 2: RAG-based CBT technique retriever |
| [`cbt-backend/agents/therapy_response.py`](../cbt-backend/agents/therapy_response.py) | Agent 3: Therapy response generator |
| [`cbt-backend/memory/session_memory.py`](../cbt-backend/memory/session_memory.py) | Per-session conversation memory |
| [`cbt-backend/memory/user_memory_faiss.py`](../cbt-backend/memory/user_memory_faiss.py) | Long-term user emotional pattern memory |
| [`cbt-backend/safety/enhanced_safety.py`](../cbt-backend/safety/enhanced_safety.py) | Crisis detection & safety module |
| [`cbt-backend/agents/multilingual_utils.py`](../cbt-backend/agents/multilingual_utils.py) | Hinglish TTS text enhancement |
| [`cbt-backend/agents/ssml_generator.py`](../cbt-backend/agents/ssml_generator.py) | Google Cloud SSML generation |
| [`cbt-backend/rag/retriever_faiss.py`](../cbt-backend/rag/retriever_faiss.py) | FAISS vector retriever |
| [`cbt-backend/requirements.txt`](../cbt-backend/requirements.txt) | Python dependencies |

---

## 🔄 Voice Session Pipeline (10 Steps)

```
1. User speaks → Audio recorded in browser (WebM/MP3)
2. Audio uploaded → POST /voice-session (FastAPI)
3. Google Cloud STT → Transcript (Hindi + English multilingual)
4. Enhanced Safety Check → Crisis detection
5. Agent 1: CBT Analyzer → Emotions, distortions identified
6. Agent 2: Evidence Collector → RAG retrieves relevant CBT techniques
7. Memory Context → Last 5 session turns + long-term user patterns
8. Agent 3: Therapy Generator → Personalized response via local LLM
9. Multilingual Enhancement → Hinglish text processing
10. Google Cloud TTS → Neural2 voice synthesis → MP3 audio returned
```

---

## 🧩 Feature Breakdown

### 1. Google Cloud Speech-to-Text (STT)
- **Primary language**: `hi-IN` (Hindi)
- **Fallback languages**: `en-IN`, `en-US`
- **Model**: `latest_long` + enhanced mode
- Auto-punctuation enabled
- Supports WebM, MP3, WAV audio formats
- Concatenates multiple STT results for long utterances

```python
config = {
    "language_code": "hi-IN",
    "alternative_language_codes": ["en-IN", "en-US"],
    "enable_automatic_punctuation": True,
    "model": "latest_long",
    "use_enhanced": True,
}
```

### 2. Multi-Agent CBT Architecture

**Agent 1: Analyzer**
- Detects emotions in the transcript (`fear`, `sadness`, `anger`, etc.)
- Identifies cognitive distortions (`catastrophizing`, `all-or-nothing thinking`, etc.)
- Returns structured analysis dict

**Agent 2: Evidence Collector**
- Takes the analysis output
- Queries FAISS vector database for matching CBT techniques
- Returns relevant therapeutic interventions + RAG context

**Agent 3: Therapy Generator**
- Input: transcript + analysis + evidence + memory + optional emotion (facial)
- Generates a warm, empathetic CBT-style therapy response
- Response is conversational Hinglish or English

### 3. FAISS-Based RAG Knowledge Base
- **195,000+ CBT knowledge chunks** (enhanced retriever)
- Fallback to smaller `cbt_knowledge.index` if enhanced unavailable
- FAISS cosine similarity search over sentence embeddings
- Returns top-k relevant therapy techniques per query

```python
from rag.retriever_generated import get_enhanced_retriever
retriever = get_enhanced_retriever()
# retriever.index.ntotal → number of loaded chunks
```

### 4. Session Memory System
- **Session Memory** (`session_memory.py`): Stores last 5 conversation turns per session
- **User Memory** (`user_memory_faiss.py`): Long-term tracking of:
  - Emotional trends over time
  - Recurring cognitive distortions
  - Progress indicators

```python
memory_manager.add_exchange(
    session_id=session_id,
    user_message=transcript,
    assistant_message=therapy_response,
    user_id=user_id,
    analysis=analysis  # emotions + distortions stored
)
```

### 5. Enhanced Safety Module
- Checks every transcript for crisis signals before therapy generation
- Detects: self-harm ideation, suicidal language, acute distress
- If unsafe: bypasses therapy pipeline → delivers crisis response
- Crisis response is synthesized and returned as audio

```python
is_safe, risk_assessment = safety_checker.check_safety(
    transcript, conversation_history
)
if not is_safe:
    crisis_text = safety_checker.get_crisis_response()
```

### 6. Google Cloud Text-to-Speech (TTS)
Neural2 voice models used:

| Language | Voice | Quality |
|----------|-------|---------|
| `en-US` | `en-US-Neural2-D` | Standard US English (male) |
| `en-IN` | `en-IN-Neural2-B` | Indian English — best for Hinglish |
| `hi-IN` | `hi-IN-Neural2-B` | Hindi Neural2 (male) |

SSML prosody settings for natural Hinglish rhythm:
```xml
<speak>
  <prosody rate="105%" pitch="-0.5st">
    {therapy_response}
  </prosody>
</speak>
```

### 7. Hinglish Multilingual Enhancement
`agents/multilingual_utils.py` pre-processes therapy text before TTS:
- Normalizes transliterated Hindi words for better pronunciation
- Selects optimal language code (`en-IN` vs `hi-IN`) based on script ratio
- Ensures smooth natural-sounding mixed-language synthesis

### 8. Emotion-Adaptive Responses (Facial Detection Integration)
The `/voice-session` endpoint accepts an optional `emotion` form field:
```python
emotion: str = Form(None)  # JSON: {"emotion": "sad", "confidence": 0.87}
```
This visual emotion data is passed to the therapy generator to make responses context-aware (e.g., gentler tone when facial sadness detected).

---

## 🔌 API Endpoints

### `POST /voice-session`
**Request:** `multipart/form-data`
- `file`: Audio file (WebM/MP3/WAV)
- `language`: Language hint (`hi-IN`, `en-IN`)
- `session_id`: Unique session identifier
- `user_id`: Optional user ID for long-term memory
- `emotion`: Optional JSON string (`{"emotion": "sad", "confidence": 0.87}`)

**Response:** `audio/mpeg` (MP3 file, therapy response as speech)

### `GET /`
Health check — returns service status and available features.

---

## 🏗️ Architecture

```
                    ┌──────────────────────────────┐
                    │   Browser (React Frontend)    │
                    │   Records audio → WebM        │
                    └──────────────┬───────────────┘
                                   │ POST multipart/form-data
                                   ↓
                    ┌──────────────────────────────┐
                    │   FastAPI (port 8002)         │
                    │   cbt-backend/app.py          │
                    └──────┬───────────┬───────────┘
                           │           │
               ┌───────────▼──┐  ┌─────▼─────────────┐
               │ Google STT   │  │  Safety Checker    │
               │ (hi-IN + en) │  │  (Crisis detect)   │
               └───────────┬──┘  └────────────────────┘
                           │
               ┌───────────▼──────────────────────────┐
               │          Multi-Agent Pipeline         │
               │  Agent 1: Analyze emotions/distortions│
               │  Agent 2: RAG (FAISS 195k chunks)     │
               │  Agent 3: Generate therapy response   │
               └───────────┬──────────────────────────┘
                           │
               ┌───────────▼──┐
               │  Multilingual │
               │  Enhancement  │
               │  + SSML Gen   │
               └───────────┬──┘
                           │
               ┌───────────▼──┐
               │ Google TTS   │
               │ Neural2 voice│
               └───────────┬──┘
                           │ MP3 audio
                           ↓
                    Browser plays response
```

---

## ⚙️ Setup

### Prerequisites
```bash
# Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"

# Or set in app.py:
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../vaani-474822-service-account.json"
```

### Python Environment
```bash
cd cbt-backend
python -m venv venv_311
venv_311/Scripts/activate   # Windows
pip install -r requirements.txt
```

### Running the Service
```bash
cd cbt-backend
python app.py   # Starts on port 8002
```

Or via batch script:
```batch
run_cbt_backend.bat
```

---

## 📊 Tech Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI + Uvicorn |
| STT | Google Cloud Speech-to-Text v1p1beta1 |
| TTS | Google Cloud Text-to-Speech Neural2 |
| LLM | Local Ollama (via HTTP) |
| Vector DB | FAISS (Facebook AI Similarity Search) |
| Embeddings | Sentence Transformers |
| Memory | FAISS + JSON session store |
| Language | Python 3.11 |
| Audio | aiofiles (async), MP3 output |

---

## 🧪 Testing

```bash
cd cbt-backend
python test_therapy.py      # Test therapy pipeline
python test_voice.py        # Test voice roundtrip
python test_tts_endpoint.py # Test TTS endpoint
python diagnose_voice_pipeline.py  # Full diagnostic
```
