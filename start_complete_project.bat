@echo off
setlocal enabledelayedexpansion
title Sanjeevani Project Launcher

echo ========================================================================
echo              SANJEEVANI - ULTIMATE PROJECT LAUNCHER
echo ========================================================================
echo.
echo This script will start ALL modules:
echo   1. Main Backend API (Port 5000)
echo   2. Pharmacy Support Backend (Port 8000)
echo   3. CBT/Therapy Backend (Port 8002)
echo   4. OCR Service (Port 5001)
echo   5. Avatar Bridge (Port 8001/8765)
echo   6. TalkingHead Avatar (Port 8080)
echo   7. June Voice Assistant
echo   8. Main Frontend (Port 3000)
echo.

REM Check for Ollama
echo [CHECK] Verifying Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Ollama is running.
) else (
    echo [WARNING] Ollama is NOT running! 
    echo Please run 'ollama serve' in a separate terminal.
    echo The AI features will not work without it.
    pause
)

echo.
echo [CLEANUP] Stopping existing processes on project ports...
for %%p in (3000 5000 5001 8000 8001 8002 8080 8765) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%p" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo [OK] Ports cleared.
echo.

echo [STARTING SERVICES]...

REM 1. Main Backend
echo [1/8] Starting Main Backend...
start "1. Main Backend (5000)" cmd /k "cd /d %~dp0backend && color 0E && title Main Backend && npm start"

REM 2. Pharmacy Support Backend
echo [2/8] Starting Pharmacy Support Backend...
start "2. Pharmacy Backend (8000)" cmd /k "cd /d %~dp0pharmacy-support\backend && color 0B && title Pharmacy Backend && uvicorn main:app --reload --port 8000"

REM 3. CBT Backend
echo [3/8] Starting CBT Backend...
start "3. CBT Backend (8002)" cmd /k "cd /d %~dp0cbt-backend && color 0D && title CBT Backend && python app.py"

REM 4. OCR Service
echo [4/8] Starting OCR Service...
start "4. OCR Service (5001)" cmd /k "cd /d %~dp0prescriptionAnalysis\MediScribe-OCR && color 0A && title OCR Service && python app.py"

REM 5. Avatar Bridge
echo [5/8] Starting Avatar Bridge...
if exist "%~dp0talking_june\Avatar\bridge_server.py" (
    start "5. Avatar Bridge" cmd /k "cd /d %~dp0talking_june\Avatar && color 03 && title Avatar Bridge && python bridge_server.py"
) else (
    echo [SKIP] Avatar Bridge not found.
)

REM 6. TalkingHead Avatar
echo [6/8] Starting TalkingHead Avatar...
if exist "%~dp0talking_june\Avatar\TalkingHead" (
    start "6. TalkingHead Avatar (8080)" cmd /k "cd /d %~dp0talking_june\Avatar\TalkingHead && color 0C && title TalkingHead && python -m http.server 8080"
) else (
    echo [SKIP] TalkingHead not found.
)

REM 7. June Voice Assistant
echo [7/8] Starting June Voice Assistant...
if exist "%~dp0talking_june\Avatar\june" (
    REM Set Credentials
    if exist "%~dp0vaani-474822-36de07e0981f.json" (
        set GOOGLE_APPLICATION_CREDENTIALS=%~dp0vaani-474822-36de07e0981f.json
    )
    start "7. June Voice Assistant" cmd /k "cd /d %~dp0talking_june\Avatar\june && color 0F && title June VA && python -m june_va"
) else (
    echo [SKIP] June VA not found.
)

REM 8. Frontend
echo [8/8] Starting Main Frontend...
start "8. Frontend (3000)" cmd /k "cd /d %~dp0 && color 09 && title Frontend && npm run dev"

echo.
echo ========================================================================
echo [SUCCESS] All command windows launched!
echo.
echo Please wait approx 10-20 seconds for all services to initialize.
echo The frontend will be available at: http://localhost:3000
echo ========================================================================
pause
