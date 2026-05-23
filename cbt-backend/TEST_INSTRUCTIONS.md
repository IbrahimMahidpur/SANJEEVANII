# Voice Pipeline Debug Summary

## Current Status
- ✅ Backend running with extensive debug logging
- ✅ Frontend has timeslice recording (1000ms chunks)
- ✅ STT configured to concatenate all results
- ✅ LLM response length increased to 2048 tokens

## Testing Instructions

### Step 1: Test Voice Input
1. Open: http://localhost:3000/cbt
2. Click "Tap to Speak"
3. Say: "mujhe bahut dukh ho raha hai"
4. Click button again to stop

### Step 2: Check Logs

**Frontend Console (F12)**:
- Look for: "[CBT] Data chunk received"
- Check audio blob size

**Backend Terminal**:
- Look for: "[Session xxx] Transcript: '...'"
- Check if transcript matches what you said

### Step 3: Report Back
Share:
1. Frontend console output
2. Backend terminal output  
3. What response you received

This will help identify the exact issue in the pipeline.
