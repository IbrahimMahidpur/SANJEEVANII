# 🩺 SANJEEVANI MODULE - TESTING GUIDE

## ✅ Current Status

All services are **RUNNING** and ready for testing!

### Backend Services (All Running ✅)
1. **Bridge Server** - WebSocket on `ws://localhost:8765` ✅
2. **TalkingHead Avatar** - HTTP on `http://localhost:8080` ✅
3. **June VA** - Voice Assistant Backend ✅
4. **Audio Server** - HTTP on `http://localhost:8001` ✅

### Frontend Service
- **React App** - Running on `http://localhost:3001` ✅

---

## 🚀 How to Test Sanjeevani

### Step 1: Open the Application
Open your browser and navigate to:
```
http://localhost:3001
```

### Step 2: Navigate to Sanjeevani Module
- Click the **Menu** button (usually top-right corner)
- Select **"Sanjeevani"** from the menu options
- Or directly navigate to: `http://localhost:3001/sanjeevani`

### Step 3: Start the Conversation
1. You'll see the Sanjeevani Avatar interface
2. Click the **"✨ Start Conversation"** button at the bottom
3. **Allow microphone access** when browser prompts you

### Step 4: Talk to the Avatar
1. Speak clearly into your microphone
2. You can speak in:
   - **English**: "Hello, how are you?"
   - **Hindi**: "मुझे मदद चाहिए"
   - **Hinglish**: "Hey June, kaise ho?"

3. The Avatar will:
   - Listen to your voice
   - Process it with AI (GPT-OSS 120B)
   - Respond with voice
   - Show lip-sync animation

### Step 5: End the Session
- Click the **"End Session"** button to stop the conversation
- You can start a new conversation anytime

---

## 🎯 What to Test

### ✅ Basic Functionality
- [ ] Avatar loads correctly
- [ ] "Start Conversation" button works
- [ ] Microphone permission is granted
- [ ] Voice input is detected
- [ ] Avatar responds with voice
- [ ] Lip-sync animation works
- [ ] "End Session" button works

### ✅ Voice Interaction
- [ ] Test English speech
- [ ] Test Hindi speech
- [ ] Test Hinglish (mixed) speech
- [ ] Test different volumes
- [ ] Test in quiet environment
- [ ] Test with background noise

### ✅ AI Responses
- [ ] Avatar gives relevant responses
- [ ] Responses are in appropriate language
- [ ] Voice quality is good
- [ ] Lip-sync matches the speech

### ✅ Connection Stability
- [ ] WebSocket connection is stable
- [ ] No disconnection errors
- [ ] Auto-reconnect works if disconnected
- [ ] Multiple conversations work

---

## 🔧 Troubleshooting

### Issue: "Connecting..." message doesn't change
**Solution:**
1. Check if backend services are running
2. Run: `CHECK_SANJEEVANI_STATUS.bat`
3. If services are down, run: `START_SANJEEVANI_COMPLETE.bat`

### Issue: No audio playing
**Solution:**
1. Make sure you clicked "Start Conversation"
2. Check browser audio is not muted
3. Check system volume
4. Try refreshing the page

### Issue: Microphone not working
**Solution:**
1. Check browser permissions for microphone
2. Test microphone in other apps
3. Speak louder or closer to mic
4. Check Windows microphone settings

### Issue: Avatar not visible
**Solution:**
1. Check if TalkingHead is running on port 8080
2. Try accessing directly: `http://localhost:8080`
3. Refresh the Sanjeevani page
4. Clear browser cache

### Issue: Lip-sync not working
**Solution:**
1. Wait for audio to fully load
2. Check internet connection (for Google Cloud TTS)
3. Try a different browser (Chrome recommended)

---

## 📊 Service Ports Reference

| Service | Port | URL | Status |
|---------|------|-----|--------|
| Bridge Server | 8765 | ws://localhost:8765 | ✅ Running |
| TalkingHead | 8080 | http://localhost:8080 | ✅ Running |
| Audio Server | 8001 | http://localhost:8001 | ✅ Running |
| React Frontend | 3001 | http://localhost:3001 | ✅ Running |

---

## 🎬 Quick Start Commands

### Start All Services
```cmd
START_SANJEEVANI_COMPLETE.bat
```

### Check Service Status
```cmd
CHECK_SANJEEVANI_STATUS.bat
```

### Start Only Backend
```cmd
start_sanjeevani_backend.bat
```

### Start Only Frontend
```cmd
npm run dev
```

---

## 💡 Testing Tips

1. **Best Environment**: Test in a quiet room for best voice recognition
2. **Browser**: Chrome or Edge recommended for best compatibility
3. **Microphone**: Use a good quality microphone for better results
4. **Internet**: Stable internet needed for Google Cloud services
5. **Keep Windows Open**: Don't close the terminal windows while testing

---

## 🎯 Expected Behavior

### Normal Flow:
1. User clicks "Start Conversation"
2. Button changes to "End Session" with pulsing indicator
3. User speaks into microphone
4. Avatar processes speech (may take 2-5 seconds)
5. Avatar responds with voice and lip-sync
6. User can continue conversation
7. User clicks "End Session" to stop

### Performance:
- **Response Time**: 2-5 seconds typical
- **Voice Quality**: Clear, natural-sounding
- **Lip-Sync**: Smooth, synchronized with audio
- **Connection**: Stable, auto-reconnects if dropped

---

## 📝 Test Scenarios

### Scenario 1: Basic Greeting
- **Input**: "Hello, how are you?"
- **Expected**: Avatar greets back in English

### Scenario 2: Hindi Conversation
- **Input**: "मुझे मदद चाहिए"
- **Expected**: Avatar responds in Hindi

### Scenario 3: Hinglish Mix
- **Input**: "Hey June, aaj kaisa din hai?"
- **Expected**: Avatar responds in Hinglish

### Scenario 4: Medical Query
- **Input**: "I have a headache, what should I do?"
- **Expected**: Avatar provides health advice

### Scenario 5: Multiple Turns
- **Input**: Have a 3-4 turn conversation
- **Expected**: Avatar maintains context

---

## ✅ Success Criteria

The Sanjeevani module is working correctly if:
- ✅ All 4 backend services are running
- ✅ Frontend loads without errors
- ✅ Avatar is visible and animated
- ✅ Voice input is detected
- ✅ AI responses are relevant
- ✅ Voice output is clear
- ✅ Lip-sync is synchronized
- ✅ Session can be started and stopped
- ✅ Multiple conversations work

---

## 🎉 Ready to Test!

**Everything is set up and running!**

1. Open: `http://localhost:3001`
2. Navigate to Sanjeevani
3. Click "Start Conversation"
4. Start talking!

**Enjoy testing the Sanjeevani Avatar! 🎭**
