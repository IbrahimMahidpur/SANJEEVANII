@echo off
setlocal enabledelayedexpansion
echo ========================================================================
echo              SANJEEVANI - COMPLETE PROJECT LAUNCHER
echo                    (Including June VA Backend)
echo ========================================================================
echo.
echo This script will start ALL modules and services:
echo   - Chatbot (AI Medical Assistant)
echo   - Sanjeevani (Avatar Voice Assistant with June VA)
echo   - OCR (Prescription Analysis)
echo   - Pharmacy Support (Frontend + Backend)
echo   - Community Forum
echo   - CBT Module
echo   - Outbreak Alerts
echo   - All Backend Services
echo.
echo ========================================================================
echo.

REM Check if Ollama is running
echo [PREREQUISITE] Checking Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ Ollama is running
) else (
    echo ⚠️  WARNING: Ollama is NOT running!
    echo    Please start Ollama in another terminal: ollama serve
    echo    The chatbot and June VA will not work without it.
    echo.
    pause
)

echo.
echo ========================================================================
echo Starting All Services...
echo ========================================================================
echo.

REM Kill any existing processes on required ports
echo [CLEANUP] Stopping any existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8765" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✅ Cleanup complete
echo.

REM Start Backend (Node.js API)
echo [1/6] Starting Backend API Server...
start "Sanjeevani Backend API" cmd /k "cd /d %~dp0backend && color 0E && echo ========================================== && echo    BACKEND API SERVER && echo    Port: 5000 && echo ========================================== && echo. && npm start"
timeout /t 3 /nobreak >nul
echo ✅ Backend API started on http://localhost:5000
echo.

REM Start Frontend (React/Vite)
echo [2/6] Starting Frontend (All Modules)...
start "Sanjeevani Frontend" cmd /k "cd /d %~dp0 && color 0B && echo ========================================== && echo    FRONTEND (REACT/VITE) && echo    Port: 3000 && echo ========================================== && echo. && npm run dev"
timeout /t 3 /nobreak >nul
echo ✅ Frontend started on http://localhost:3000
echo.

REM Start OCR Service (Flask/Python)
echo [3/6] Starting OCR Service (MediScribe)...
start "OCR Service - MediScribe" cmd /k "cd /d %~dp0prescriptionAnalysis\MediScribe-OCR && color 0D && echo ========================================== && echo    OCR SERVICE (MEDISCRIBE) && echo    Port: 5001 && echo ========================================== && echo. && python app.py"
timeout /t 3 /nobreak >nul
echo ✅ OCR Service started on http://localhost:5001
echo.

REM Start Avatar Bridge Server
echo [4/6] Starting Avatar Bridge Server...
cd /d %~dp0talking_june\Avatar
if exist "bridge_server.py" (
    start "Avatar Bridge Server" cmd /k "cd /d %~dp0talking_june\Avatar && color 0A && echo ========================================== && echo    AVATAR BRIDGE SERVER && echo    WebSocket: ws://localhost:8765 && echo    HTTP: http://localhost:8001 && echo ========================================== && echo. && python bridge_server.py"
    timeout /t 3 /nobreak >nul
    echo ✅ Avatar Bridge Server started
    echo    - WebSocket: ws://localhost:8765
    echo    - HTTP: http://localhost:8001
) else (
    echo ⚠️  Avatar Bridge Server not found, skipping...
)
echo.

REM Start TalkingHead Avatar
echo [5/6] Starting TalkingHead Avatar...
cd /d %~dp0talking_june\Avatar
if exist "TalkingHead" (
    start "TalkingHead Avatar" cmd /k "cd /d %~dp0talking_june\Avatar\TalkingHead && color 0C && echo ========================================== && echo    TALKINGHEAD AVATAR && echo    Port: 8080 && echo ========================================== && echo. && python -m http.server 8080"
    timeout /t 3 /nobreak >nul
    echo ✅ TalkingHead Avatar started on http://localhost:8080
) else (
    echo ⚠️  TalkingHead not found, skipping...
)
echo.

REM Start June VA (Voice Assistant Backend)
echo [6/6] Starting June VA (Voice Assistant Backend)...
cd /d %~dp0talking_june\Avatar
if exist "june" (
    REM Check which config to use
    if exist "june\config-enhanced-multilingual.json" (
        set CONFIG_FILE=config-enhanced-multilingual.json
        echo ✨ Using ENHANCED configuration for maximum accuracy!
    ) else if exist "june\config.json" (
        set CONFIG_FILE=config.json
        echo ℹ️  Using standard configuration
    ) else (
        echo ⚠️  Config file not found, using default
        set CONFIG_FILE=config.json
    )
    
    REM Set Google Cloud credentials if available
    if exist "%~dp0talking_june\Avatar\vaani-474822-49ec0963711e.json" (
        set GOOGLE_APPLICATION_CREDENTIALS=%~dp0talking_june\Avatar\vaani-474822-49ec0963711e.json
        echo ✅ Google Cloud credentials loaded
    ) else if exist "%~dp0vaani-474822-36de07e0981f.json" (
        set GOOGLE_APPLICATION_CREDENTIALS=%~dp0vaani-474822-36de07e0981f.json
        echo ✅ Google Cloud credentials loaded (from root)
    ) else (
        echo ⚠️  Google Cloud credentials not found
    )
    
    start "June VA - Voice Assistant" cmd /k "cd /d %~dp0talking_june\Avatar\june && color 0F && echo ========================================== && echo    JUNE VA - VOICE ASSISTANT && echo    Config: !CONFIG_FILE! && echo ========================================== && echo. && python -m june_va --config !CONFIG_FILE!"
    timeout /t 3 /nobreak >nul
    echo ✅ June VA started (Voice Assistant Backend)
) else (
    echo ⚠️  June VA not found, skipping...
)
echo.

REM Start Pharmacy Support Backend
echo [7/8] Starting Pharmacy Support Backend...
cd /d %~dp0pharmacy-support\backend
if exist "main.py" (
    start "Pharmacy Support Backend" cmd /k "cd /d %~dp0pharmacy-support\backend && color 0B && echo ========================================== && echo    PHARMACY SUPPORT BACKEND && echo    Port: 8000 && echo ========================================== && echo. && uvicorn main:app --reload --port 8000"
    timeout /t 3 /nobreak >nul
    echo ✅ Pharmacy Support Backend started on http://localhost:8000
) else (
    echo ⚠️  Pharmacy Support Backend not found, skipping...
)
echo.

REM Start CBT Backend
echo [8/8] Starting CBT Backend...
cd /d %~dp0cbt-backend
if exist "app.py" (
    start "CBT Backend" cmd /k "cd /d %~dp0cbt-backend && color 0D && echo ========================================== && echo    CBT BACKEND && echo    Port: 8002 && echo ========================================== && echo. && python app.py"
    timeout /t 3 /nobreak >nul
    echo ✅ CBT Backend started on http://localhost:8002
) else (
    echo ⚠️  CBT Backend not found, skipping...
)
echo.

echo ========================================================================
echo              ALL SERVICES STARTED SUCCESSFULLY!
echo ========================================================================
echo.
echo 🌐 MAIN APPLICATION:
echo    http://localhost:3000
echo.
echo 📋 AVAILABLE MODULES:
echo    ✅ Chatbot (AI Medical Assistant)
echo       → http://localhost:3000/chat
echo.
echo    ✅ Sanjeevani (Avatar Voice Assistant)
echo       → http://localhost:3000/sanjeevani
echo       → Direct Avatar: http://localhost:8080
echo.
echo    ✅ Prescription Analysis (OCR)
echo       → http://localhost:3000/prescription-analysis
echo.
echo    ✅ Pharmacy Support (Find Doctors/Pharmacies)
echo       → http://localhost:3000/pharmacy-support
echo       → Backend: http://localhost:8000
echo.
echo    ✅ Community Forum
echo       → http://localhost:3000/community-forum
echo.
echo    ✅ CBT Module
echo       → http://localhost:3000/cbt
echo       → Backend: http://localhost:8002
echo.
echo    ✅ Outbreak Alerts
echo       → Available in the main menu
echo.
echo 🔧 BACKEND SERVICES (8 Services Running):
echo    1. Backend API:        http://localhost:5000
echo    2. OCR Service:        http://localhost:5001
echo    3. Avatar Bridge:      ws://localhost:8765
echo    4. Audio Server:       http://localhost:8001
echo    5. TalkingHead:        http://localhost:8080
echo    6. June VA:            Voice Assistant Backend
echo    7. Pharmacy Backend:   http://localhost:8000
echo    8. CBT Backend:        http://localhost:8002
echo.
echo ========================================================================
echo.
echo Opening main application in browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000
echo.
echo ========================================================================
echo.
echo ℹ️  NOTES:
echo    - Each service runs in its own colored window
echo    - Check individual windows for logs and errors
echo    - Press Ctrl+C in any window to stop that service
echo    - June VA window shows voice assistant activity
echo.
echo    To test June VA:
echo    1. Go to http://localhost:8080 (TalkingHead)
echo    2. Speak into microphone
echo    3. Avatar will respond with voice and lip-sync
echo.
echo ========================================================================
echo.
echo Press any key to close this launcher window...
echo (Services will continue running in their own windows)
pause >nul
