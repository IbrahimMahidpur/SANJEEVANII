# 🎯 SANJEEVANI MODULE - COMPLETE SETUP GUIDE

## Current Status Update

### ✅ Verified Components
1. **Ollama** - Running ✅
   - Model: `gpt-oss:120b-cloud` ✅
   - Tested and working ✅

2. **Python Dependencies** - All Installed ✅
   - PyAudio 0.2.14 ✅
   - Google Cloud Speech 2.34.0 ✅
   - Google Cloud TTS 2.33.0 ✅
   - Ollama 0.6.0 ✅
   - Websockets 12.0 ✅
   - Pygame 2.6.1 ✅

3. **Google Cloud Credentials** - Set ✅
   - File: `vaani-474822-36de07e0981f.json` ✅

4. **Backend Services** - Running ✅
   - Bridge Server (port 8765) ✅
   - TalkingHead (port 8080) ✅

5. **Frontend** - Running ✅
   - React App (port 3001) ✅

### ⚠️ Issue Found
**June VA** has been failing to start due to silent errors (likely audio device initialization in PowerShell).

### ✅ Solution Applied
Created a proper CMD-based startup script: `START_JUNE_VA.bat`

---

## 🚀 Complete Startup Procedure

### Method 1: All-in-One (Recommended)
```cmd
START_SANJEEVANI_COMPLETE.bat
```
Then manually start June VA:
```cmd
START_JUNE_VA.bat
```

### Method 2: Individual Services
```cmd
REM 1. Start Backend Services
cd c:\Users\imahi\gpt\talking_june\Avatar
RUN_COMPLETE_PROJECT.bat

REM 2. Start Frontend
cd c:\Users\imahi\gpt
npm run dev

REM 3. Navigate to http://localhost:3001/sanjeevani
```

---

## 🎤 Testing Sanjeevani

### Step 1: Verify All Services
Run this to check status:
```cmd
CHECK_SANJEEVANI_STATUS.bat
```

You should see:
- ✅ Bridge Server (port 8765)
- ✅ TalkingHead (port 8080)
- ✅ Audio Server (port 8001)
- ✅ Frontend (port 3001)

### Step 2: Check June VA Window
The June VA window should show:
```
✓ Google Cloud Text-to-Speech API validated
✓ Google Cloud Speech-to-Text API validated
⏸️  Starting in PAUSED state - Waiting for Sanjeevani module...
[WS] ✅ Connected to bridge server
```

### Step 3: Open Sanjeevani
1. Open browser: `http://localhost:3001`
2. Navigate to **Sanjeevani** module
3. Click **"✨ Start Conversation"**
4. Allow microphone access

### Step 4: Talk to Avatar
Speak clearly in:
- **English**: "Hello, how are you?"
- **Hindi**: "नमस्ते, आप कैसे हैं?"
- **Hinglish**: "Hey, kaise ho?"

### Step 5: Observe the Flow
1. **You speak** → Microphone captures
2. **June VA** → Converts speech to text (STT)
3. **Ollama** → Processes with gpt-oss:120b-cloud
4. **June VA** → Converts response to speech (TTS)
5. **Bridge** → Sends audio to TalkingHead
6. **Avatar** → Speaks with lip-sync animation

---

## 🔍 Troubleshooting

### Issue: June VA window shows error
**Check for:**
- `Invalid ollama model` → Run: `ollama pull gpt-oss:120b-cloud`
- `PyAudio not installed` → Run: `pip install pyaudio`
- `Google Cloud API not enabled` → Enable APIs in Google Cloud Console
- `Credentials not found` → Check file path

### Issue: No voice response
**Verify:**
1. June VA is running (check window)
2. Bridge server shows connections
3. Microphone is working
4. Speak louder or closer to mic

### Issue: Avatar not visible
**Fix:**
1. Check TalkingHead on port 8080
2. Refresh Sanjeevani page
3. Clear browser cache

### Issue: Connection errors
**Fix:**
1. Restart all services: `RESTART_SANJEEVANI.bat`
2. Check firewall settings
3. Ensure ports are not blocked

---

## 📊 Service Architecture

```
┌─────────────────┐
│  User (Voice)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Microphone    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│       JUNE VA               │
│  ┌───────────────────────┐  │
│  │ Google Cloud STT      │  │
│  │ (Speech-to-Text)      │  │
│  └───────────┬───────────┘  │
│              │              │
│              ▼              │
│  ┌───────────────────────┐  │
│  │ Ollama LLM            │  │
│  │ (gpt-oss:120b-cloud)  │  │
│  └───────────┬───────────┘  │
│              │              │
│              ▼              │
│  ┌───────────────────────┐  │
│  │ Google Cloud TTS      │  │
│  │ (Text-to-Speech)      │  │
│  └───────────┬───────────┘  │
└──────────────┼──────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Bridge Server            │
│     (WebSocket)              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     TalkingHead Avatar       │
│     (3D Animation)           │
└──────────────────────────────┘
               │
               ▼
┌──────────────────────────────┐
│     React Frontend           │
│     (Sanjeevani Module)      │
└──────────────────────────────┘
```

---

## 📝 Files Created

1. **START_JUNE_VA.bat** - Proper June VA startup with error checking
2. **START_SANJEEVANI_COMPLETE.bat** - Start all services
3. **RESTART_SANJEEVANI.bat** - Restart all services
4. **CHECK_SANJEEVANI_STATUS.bat** - Check service status
5. **SANJEEVANI_DIAGNOSIS.md** - Troubleshooting guide
6. **SANJEEVANI_TESTING_GUIDE.md** - Testing procedures

---

## ✅ Next Steps

1. **Check the June VA window** that just opened
   - Look for any error messages
   - Verify it says "Connected to bridge server"

2. **If June VA is running successfully:**
   - Open `http://localhost:3001/sanjeevani`
   - Click "Start Conversation"
   - Start talking!

3. **If there are errors:**
   - Share the error message from the June VA window
   - I'll provide the exact fix

---

## 🎯 Expected Behavior When Working

### June VA Window:
```
✓ Google Cloud Text-to-Speech API validated
✓ Google Cloud Speech-to-Text API validated
⏸️  Starting in PAUSED state - Waiting for Sanjeevani module...
[WS] ✅ Connected to bridge server
[BridgeListener] Resumed capture from bridge
🗣️ User said (hi-IN): "Hello, how are you?"
🎤 TTS Voice: HI-IN for text: 'Hello! I'm doing well...'
⚡ Audio Delivery: 245ms
```

### Browser (Sanjeevani):
- Avatar visible
- "Start Conversation" button works
- Microphone indicator active
- Avatar speaks and lip-syncs

---

**🎭 Ready to test! Check the June VA window and let me know what you see!**
