@echo off
title SANJEEVANI - One-Click Launcher
color 0A
cls

echo.
echo ========================================================================
echo                    SANJEEVANI - ONE CLICK LAUNCHER
echo ========================================================================
echo.
echo Starting all services in one go...
echo.

REM Check Ollama
echo [CHECK] Verifying Ollama is running...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Ollama is running
) else (
    echo [ERROR] Ollama is NOT running!
    echo.
    echo Please start Ollama first:
    echo   1. Open a new terminal
    echo   2. Run: ollama serve
    echo.
    echo Press any key to exit...
    pause >nul
    exit
)

echo.
echo [CLEANUP] Killing any existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8765" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8002" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Cleanup complete

echo.
echo ========================================================================
echo                    STARTING ALL SERVICES (7 Total)
echo ========================================================================
echo.

REM 1. Backend API
echo [1/6] Starting Backend API (Port 5000)...
start "Backend API" /MIN cmd /k "cd /d %~dp0backend && color 0E && npm start"
timeout /t 2 /nobreak >nul

REM 2. Frontend
echo [2/6] Starting Frontend (Port 3000)...
start "Frontend" /MIN cmd /k "cd /d %~dp0 && color 0B && npm run dev"
timeout /t 2 /nobreak >nul

REM 3. OCR Service
echo [3/6] Starting OCR Service (Port 5001)...
start "OCR Service" /MIN cmd /k "cd /d %~dp0prescriptionAnalysis\MediScribe-OCR && color 0D && python app.py"
timeout /t 2 /nobreak >nul

REM 4. Avatar Bridge
echo [4/6] Starting Avatar Bridge (Port 8765/8001)...
if exist "%~dp0talking_june\Avatar\bridge_server.py" (
    start "Avatar Bridge" /MIN cmd /k "cd /d %~dp0talking_june\Avatar && color 0A && python bridge_server.py"
    timeout /t 2 /nobreak >nul
) else (
    echo [SKIP] Avatar Bridge not found
)

REM 5. TalkingHead
echo [5/6] Starting TalkingHead Avatar (Port 8080)...
if exist "%~dp0talking_june\Avatar\TalkingHead" (
    start "TalkingHead" /MIN cmd /k "cd /d %~dp0talking_june\Avatar\TalkingHead && color 0C && python -m http.server 8080"
    timeout /t 2 /nobreak >nul
) else (
    echo [SKIP] TalkingHead not found
)

REM 6. June VA
echo [6/7] Starting June VA Voice Assistant...
if exist "%~dp0talking_june\Avatar\june" (
    if exist "%~dp0vaani-474822-36de07e0981f.json" (
        set GOOGLE_APPLICATION_CREDENTIALS=%~dp0vaani-474822-36de07e0981f.json
    )
    start "June VA" /MIN cmd /k "cd /d %~dp0talking_june\Avatar\june && color 0F && python -m june_va --config config-enhanced-multilingual.json"
    timeout /t 2 /nobreak >nul
) else (
    echo [SKIP] June VA not found
)

REM 7. CBT Backend
echo [7/7] Starting CBT Backend (Port 8002)...
if exist "%~dp0cbt-backend" (
    start "CBT Backend" /MIN cmd /k "cd /d %~dp0cbt-backend && color 0D && python app.py"
    timeout /t 2 /nobreak >nul
) else (
    echo [SKIP] CBT Backend not found
)

echo.
echo ========================================================================
echo                    ALL SERVICES STARTED!
echo ========================================================================
echo.
echo Waiting 10 seconds for services to initialize...
timeout /t 10 /nobreak >nul

echo.
echo Opening browser...
start http://localhost:3000

cls
echo.
echo ========================================================================
echo                    SANJEEVANI IS NOW RUNNING!
echo ========================================================================
echo.
echo [MAIN APP]        http://localhost:3000
echo.
echo [MODULES]
echo   - Chatbot:              http://localhost:3000/chat
echo   - Sanjeevani Avatar:    http://localhost:3000/sanjeevani
echo   - Prescription OCR:     http://localhost:3000/prescription-analysis
echo   - Pharmacy Support:     http://localhost:3000/pharmacy-support
echo   - Outbreak Alerts:      http://localhost:3000/outbreak-alerts
echo   - Direct Avatar:        http://localhost:8080
echo.
echo [BACKEND SERVICES]
echo   - Backend API:          http://localhost:5000
echo   - OCR Service:          http://localhost:5001
echo   - Avatar Bridge:        ws://localhost:8765
echo   - Audio Server:         http://localhost:8001
echo.
echo ========================================================================
echo.
echo All services are running in minimized windows.
echo To stop all services, close this window or press Ctrl+C.
echo.
echo ========================================================================
echo.
pause
