# Sanjeevani Avatar Integration - README

## 🩺 What is Sanjeevani?

Sanjeevani is an AI-powered Avatar Assistant that combines:
- **3D Avatar** with realistic lip-sync animation
- **Voice Recognition** (Google Cloud Speech-to-Text)
- **AI Chatbot** (GPT-OSS 120B Cloud model via Ollama)
- **Text-to-Speech** (Google Cloud TTS)

## 🚀 How to Use

### Step 1: Start Backend Services

**Option A - Easy Way:**
```cmd
start_sanjeevani_backend.bat
```

**Option B - Manual:**
```cmd
cd talking_june\Avatar
RUN_COMPLETE_PROJECT.bat
```

This will start:
1. **Bridge Server** (WebSocket on port 8765, HTTP on port 8001)
2. **TalkingHead Frontend** (port 8080)
3. **June VA** (Voice Assistant backend)

### Step 2: Start React App

```cmd
npm run dev
```

### Step 3: Access Sanjeevani

1. Open your React app (usually http://localhost:5173)
2. Click the **Menu** button (top-right)
3. Select **"Sanjeevani"** from the menu
4. Click the **blue button** in the Avatar interface to activate audio
5. Start talking!

## 🎤 Using the Avatar

1. **Activate Audio**: Click the blue button when you first load the page
2. **Speak Clearly**: Talk into your microphone
3. **Wait for Response**: The Avatar will process your speech and respond
4. **Watch Lip-Sync**: The Avatar's mouth will move in sync with the voice

## 🔧 Troubleshooting

### "Backend Not Running" Message

**Solution**: Start the backend services using `start_sanjeevani_backend.bat`

### No Audio Playing

**Solution**: Make sure you clicked the blue button to activate audio in the browser

### Microphone Not Working

**Solution**: 
- Check browser permissions for microphone access
- Speak louder or closer to the microphone
- Test in a quiet environment

### Connection Issues

**Solution**:
- Make sure all 3 backend windows are running
- Check that ports 8765, 8001, and 8080 are not in use
- Refresh the Sanjeevani page

## 📁 Project Structure

```
gpt/
├── src/
│   ├── pages/
│   │   └── Sanjeevani.tsx          # Main Sanjeevani page component
│   └── App.tsx                      # Added /sanjeevani route
├── talking_june/
│   └── Avatar/
│       ├── bridge_server.py         # WebSocket bridge
│       ├── TalkingHead/             # 3D Avatar interface
│       └── june/                    # Voice assistant backend
└── start_sanjeevani_backend.bat    # Quick start script
```

## 🌐 Ports Used

- **5173**: React dev server (main app)
- **8080**: TalkingHead frontend (Avatar interface)
- **8765**: WebSocket bridge server
- **8001**: HTTP server for audio files

## 💡 Tips

- Keep all terminal windows open while using Sanjeevani
- Speak clearly and wait for the Avatar to finish responding
- The Avatar works best in a quiet environment
- You can navigate away and come back - the backend stays running

## 🔗 Integration Details

The Sanjeevani page uses:
- **iframe** to embed the TalkingHead interface
- **WebSocket** connection to the bridge server for real-time communication
- **Backend detection** to check if services are running
- **Auto-reconnect** if WebSocket connection drops

---

**Enjoy your AI Avatar Assistant! 🎭**
