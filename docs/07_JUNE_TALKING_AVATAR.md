# 🎤 Feature 7: June — Talking Avatar Voice Assistant

## Overview

**June** is an animated talking avatar voice assistant — a full end-to-end lip-synced, emotion-aware virtual character that speaks therapy responses in real time. Built with a multi-modal pipeline combining a 3D/2D animated avatar, Google Cloud TTS, Google Cloud STT, and real-time lip-sync.

The avatar is the visual face of the CBT Voice Therapy system and provides a more human, engaging interface for mental health conversations.

---

## 📁 Key Files

| File | Role |
|------|------|
| [`talking_june/Avatar/`](../talking_june/Avatar/) | Main avatar system |
| [`talking_june/Avatar/june_va/`](../talking_june/Avatar/june_va/) | Virtual assistant core |
| [`talking_june/Avatar/june_va/models/llm.py`](../talking_june/Avatar/june_va/models/) | LLM integration |
| [`talking_june/Avatar/june_va/models/stt.py`](../talking_june/Avatar/june_va/models/) | Speech-to-Text module |
| [`talking_june/Avatar/june_va/models/tts.py`](../talking_june/Avatar/june_va/models/) | Text-to-Speech module |
| [`talking_june/Avatar/june_va/language_detector.py`](../talking_june/Avatar/june_va/) | Hinglish language detection |
| [`talking_june/Avatar/june_va/utils.py`](../talking_june/Avatar/june_va/) | Utilities |
| [`talking_june/Avatar/june_va/multilingual_utils.py`](../talking_june/Avatar/june_va/) | Multilingual text processing |
| [`START_JUNE_NOW.bat`](../START_JUNE_NOW.bat) | Quick launcher |
| [`start_june_va.bat`](../start_june_va.bat) | Full VA launcher |

---

## 🧩 Features

### 1. Multi-Modal Voice Pipeline
```
Microphone input
    ↓
Google Cloud STT (Hindi + English)
    ↓
Language detection (Hindi/English/Hinglish)
    ↓
LLM therapy response generation
    ↓
Text enhancement for multilingual TTS
    ↓
Google Cloud TTS Neural2 voice synthesis
    ↓
Animated avatar lip-sync playback
```

### 2. Language Detection
`language_detector.py` detects the language of each utterance:
- **Hindi**: Devanagari script detection
- **English**: Latin script
- **Hinglish**: Mixed script / transliterated patterns

```python
# Automatic detection selects optimal TTS voice
# en-IN-Neural2-B for Hinglish (best natural sound)
# hi-IN-Neural2-B for pure Hindi
# en-US-Neural2-D for pure English
```

### 3. Talking Avatar with Lip Sync
The avatar system uses audio analysis to drive real-time lip movements:
- Audio amplitude → mouth open/close animation
- Phoneme-level synchronization for natural speech appearance
- Emotion-responsive facial expressions

### 4. Multilingual TTS Enhancement
`multilingual_utils.py` pre-processes LLM output before speech synthesis:
- Normalizes Hindi transliteration
- Removes markdown symbols
- Adjusts prosody markers for SSML
- Selects optimal language code

### 5. Full Conversation Loop
The avatar maintains context across turns:
- Greets users
- Maintains session state
- Responds empathetically to emotional cues
- Transitions smoothly between Hindi and English

---

## 🔌 Voice API (Google Cloud)

### STT Configuration
```python
config = {
    "language_code": "hi-IN",
    "alternative_language_codes": ["en-IN", "en-US"],
    "enable_automatic_punctuation": True,
    "model": "latest_long",
    "use_enhanced": True,
}
```

### TTS Voice Map
```python
VOICE_MAP = {
    "en-US": {"name": "en-US-Neural2-D", "gender": MALE},
    "en-IN": {"name": "en-IN-Neural2-B", "gender": MALE},  # Best for Hinglish
    "hi-IN": {"name": "hi-IN-Neural2-B", "gender": MALE},
}
```

---

## 🚀 Running June VA

```bash
# Quick start
START_JUNE_NOW.bat

# Full startup with all dependencies
start_june_va.bat

# Python 3.11 specific (recommended)
START_JUNE_VA_PY311.bat
```

---

## 📊 Tech Stack

| Component | Technology |
|-----------|------------|
| Avatar | Python (2D/3D animation engine) |
| STT | Google Cloud Speech-to-Text |
| TTS | Google Cloud Text-to-Speech Neural2 |
| LLM | Local Ollama |
| Language | Python 3.11 |
| Lip Sync | Audio amplitude analysis |
