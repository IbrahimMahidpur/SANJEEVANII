@echo off
echo ========================================================================
echo           SANJEEVANI - COMPLETE SYSTEM STARTUP
echo           Using gpt-oss:120b-cloud LLM Model
echo ========================================================================
echo.

REM Kill any existing processes first
echo [1/5] Cleaning up old processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✅ Cleanup complete
echo.

REM Start Bridge Server
echo [2/5] Starting Bridge Server...
cd /d c:\Users\imahi\gpt\talking_june\Avatar
start "Sanjeevani - Bridge Server" cmd /k "title Sanjeevani - Bridge Server && color 0A && python bridge_server.py"
timeout /t 3 /nobreak >nul
echo ✅ Bridge Server started (port 8765)
echo.

REM Start TalkingHead
echo [3/5] Starting TalkingHead Avatar...
start "Sanjeevani - TalkingHead" cmd /k "title Sanjeevani - TalkingHead && color 0B && cd TalkingHead && python -m http.server 8080"
timeout /t 3 /nobreak >nul
echo ✅ TalkingHead started (port 8080)
echo.

REM Start June VA
echo [4/5] Starting June VA (Voice Assistant)...
echo    Model: gpt-oss:120b-cloud
cd /d c:\Users\imahi\gpt\talking_june\Avatar\june
start "Sanjeevani - June VA" cmd /k "title Sanjeevani - June VA && color 0F && set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json && python -m june_va --config config-enhanced-multilingual.json --verbose"
timeout /t 5 /nobreak >nul
echo ✅ June VA started
echo.

REM Start Frontend
echo [5/5] Starting React Frontend...
cd /d c:\Users\imahi\gpt
start "Sanjeevani - Frontend" cmd /k "title Sanjeevani - Frontend && color 0E && npm run dev"
timeout /t 5 /nobreak >nul
echo ✅ Frontend starting...
echo.

echo ========================================================================
echo           ✅ ALL SANJEEVANI SERVICES STARTED!
echo ========================================================================
echo.
echo  Backend Services:
echo   ✅ Bridge Server:    ws://localhost:8765
echo   ✅ TalkingHead:      http://localhost:8080
echo   ✅ June VA:          gpt-oss:120b-cloud model
echo.
echo  Frontend:
echo   ✅ React App:        http://localhost:3001 (or 5173)
echo.
echo ========================================================================
echo  IMPORTANT: Check the June VA window!
echo ========================================================================
echo.
echo  The June VA window should show:
echo   ✓ Google Cloud Text-to-Speech API validated
echo   ✓ Google Cloud Speech-to-Text API validated
echo   ⏸️  Starting in PAUSED state
echo   [WS] ✅ Connected to bridge server
echo.
echo  If you see errors in June VA window, please share them!
echo.
echo ========================================================================
echo  HOW TO TEST:
echo ========================================================================
echo.
echo  1. Wait 10 seconds for all services to fully start
echo  2. Open browser: http://localhost:3001
echo  3. Navigate to Sanjeevani module
echo  4. Click "Start Conversation"
echo  5. Allow microphone access
echo  6. Speak: "Hello, how are you?"
echo.
echo  The avatar should:
echo   - Listen to your voice
echo   - Process with gpt-oss:120b-cloud AI
echo   - Respond with voice and lip-sync
echo.
echo ========================================================================
echo.
echo  Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul

start http://localhost:3001

echo.
echo  Browser opened!
echo.
echo  Keep all 5 windows open:
echo   1. This window
echo   2. Bridge Server
echo   3. TalkingHead
echo   4. June VA (CHECK THIS FOR ERRORS!)
echo   5. Frontend
echo.
echo  Press any key to close this window (services will keep running)...
pause >nul
