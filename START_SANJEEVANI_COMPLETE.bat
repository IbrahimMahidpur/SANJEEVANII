@echo off
echo ========================================================================
echo           SANJEEVANI MODULE - COMPLETE STARTUP
echo ========================================================================
echo.
echo This will start:
echo   [BACKEND]
echo   1. Bridge Server (WebSocket on port 8765)
echo   2. TalkingHead Avatar (HTTP on port 8080)
echo   3. June VA (Voice Assistant)
echo.
echo   [FRONTEND]
echo   4. React Frontend (port 5173)
echo.
echo ========================================================================
echo.

REM =======================================================================
REM STEP 1: Start Backend Services
REM =======================================================================
echo [STEP 1/2] Starting Backend Services...
echo.

cd /d "%~dp0talking_june\Avatar"

REM Check if bridge_server.py exists
if not exist "bridge_server.py" (
    echo ❌ ERROR: bridge_server.py not found!
    echo    Please check the talking_june\Avatar directory
    pause
    exit /b 1
)

REM Start Bridge Server
echo Starting Bridge Server...
start "Sanjeevani - Bridge Server" cmd /k "title Sanjeevani - Bridge Server && color 0A && python bridge_server.py"
timeout /t 3 /nobreak >nul
echo ✅ Bridge Server started on ws://localhost:8765
echo.

REM Start TalkingHead
echo Starting TalkingHead Avatar...
start "Sanjeevani - TalkingHead" cmd /k "title Sanjeevani - TalkingHead && color 0B && cd TalkingHead && python -m http.server 8080"
timeout /t 3 /nobreak >nul
echo ✅ TalkingHead started on http://localhost:8080
echo.

REM Start June VA
echo Starting June VA (Voice Assistant)...
cd june

REM Set Google Cloud credentials
set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json

REM Check which config to use
if exist "config-enhanced-multilingual.json" (
    set CONFIG_FILE=config-enhanced-multilingual.json
    echo ✨ Using Enhanced Multilingual Configuration
) else if exist "config.json" (
    set CONFIG_FILE=config.json
    echo ℹ️  Using Standard Configuration
) else (
    echo ❌ ERROR: Config file not found!
    pause
    exit /b 1
)

start "Sanjeevani - June VA" cmd /k "title Sanjeevani - June VA && color 0F && set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json && python -m june_va --config %CONFIG_FILE%"
timeout /t 3 /nobreak >nul
echo ✅ June VA started
echo.

REM =======================================================================
REM STEP 2: Start Frontend
REM =======================================================================
echo ========================================================================
echo [STEP 2/2] Starting Frontend...
echo ========================================================================
echo.

cd /d "%~dp0"

REM Check if node_modules exists
if not exist "node_modules" (
    echo ⚠️  node_modules not found. Installing dependencies...
    call npm install
    echo.
)

REM Start React dev server
echo Starting React Frontend...
start "Sanjeevani - Frontend" cmd /k "title Sanjeevani - Frontend && color 0E && npm run dev"
timeout /t 5 /nobreak >nul
echo ✅ Frontend starting...
echo.

REM =======================================================================
REM ALL SERVICES STARTED
REM =======================================================================
echo ========================================================================
echo           ✅ ALL SANJEEVANI SERVICES STARTED!
echo ========================================================================
echo.
echo  Backend Services:
echo   ✅ Bridge Server:    ws://localhost:8765
echo   ✅ TalkingHead:      http://localhost:8080
echo   ✅ June VA:          Running (Voice Assistant)
echo.
echo  Frontend:
echo   ✅ React App:        http://localhost:5173
echo.
echo ========================================================================
echo  HOW TO TEST:
echo ========================================================================
echo.
echo  1. Wait for React dev server to fully start
echo  2. Open browser: http://localhost:5173
echo  3. Navigate to Sanjeevani module from menu
echo  4. Click "Start Conversation" button
echo  5. Speak into your microphone!
echo.
echo  The avatar will:
echo   - Listen to your voice
echo   - Process with AI
echo   - Respond with voice and lip-sync animation
echo.
echo ========================================================================
echo.
echo  Press any key to open browser...
pause >nul

start http://localhost:5173

echo.
echo  Browser opened! Navigate to Sanjeevani module.
echo.
echo  Keep all terminal windows open while testing.
echo  Close this window when done.
echo.
pause
