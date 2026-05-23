@echo off
title SANJEEVANI - Complete Project Demo
color 0A
cls

echo.
echo ========================================================================
echo           SANJEEVANI - COMPLETE PROJECT DEMO LAUNCHER
echo ========================================================================
echo.
echo Starting ALL services and modules for complete demo...
echo.

REM ========================================================================
REM CLEANUP - Kill existing processes
REM ========================================================================

echo [CLEANUP] Stopping any existing services...
echo.

REM Kill by port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8765" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8002" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1

timeout /t 3 /nobreak >nul
echo [OK] Cleanup complete
echo.

REM ========================================================================
REM START SERVICES
REM ========================================================================

echo ========================================================================
echo                    STARTING ALL SERVICES (7 Total)
echo ========================================================================
echo.

REM 1. Backend API (Port 5000)
echo [1/7] Starting Backend API (Port 5000)...
if exist "%~dp0backend" (
    start "Backend API" cmd /k "cd /d %~dp0backend && color 0E && echo ========== BACKEND API (Port 5000) ========== && npm start"
    timeout /t 4 /nobreak >nul
    echo [OK] Backend API started
) else (
    echo [ERROR] Backend directory not found!
)
echo.

REM 2. Frontend (Port 3000)
echo [2/7] Starting Frontend (Port 3000)...
start "Frontend" cmd /k "cd /d %~dp0 && color 0B && echo ========== FRONTEND (Port 3000) ========== && npm run dev"
timeout /t 4 /nobreak >nul
echo [OK] Frontend started
echo.

REM 3. OCR Service (Port 5001)
echo [3/7] Starting OCR Service (Port 5001)...
if exist "%~dp0prescriptionAnalysis\MediScribe-OCR" (
    start "OCR Service" cmd /k "cd /d %~dp0prescriptionAnalysis\MediScribe-OCR && color 0D && echo ========== OCR SERVICE (Port 5001) ========== && python app.py"
    timeout /t 4 /nobreak >nul
    echo [OK] OCR Service started
) else (
    echo [SKIP] OCR Service directory not found
)
echo.

REM 4. Avatar Bridge (Port 8765/8001)
echo [4/7] Starting Avatar Bridge (Port 8765/8001)...
if exist "%~dp0talking_june\Avatar\bridge_server.py" (
    start "Avatar Bridge" cmd /k "cd /d %~dp0talking_june\Avatar && color 0A && echo ========== AVATAR BRIDGE (Port 8765/8001) ========== && python bridge_server.py"
    timeout /t 4 /nobreak >nul
    echo [OK] Avatar Bridge started
) else (
    echo [SKIP] Avatar Bridge not found
)
echo.

REM 5. TalkingHead (Port 8080)
echo [5/7] Starting TalkingHead Avatar (Port 8080)...
if exist "%~dp0talking_june\Avatar\TalkingHead" (
    start "TalkingHead" cmd /k "cd /d %~dp0talking_june\Avatar\TalkingHead && color 0C && echo ========== TALKINGHEAD (Port 8080) ========== && python -m http.server 8080"
    timeout /t 4 /nobreak >nul
    echo [OK] TalkingHead started
) else (
    echo [SKIP] TalkingHead directory not found
)
echo.

REM 6. June VA (Voice Assistant)
echo [6/7] Starting June VA (Voice Assistant)...
if exist "%~dp0talking_june\Avatar\june" (
    if exist "%~dp0vaani-474822-36de07e0981f.json" (
        set GOOGLE_APPLICATION_CREDENTIALS=%~dp0vaani-474822-36de07e0981f.json
    )
    start "June VA" cmd /k "cd /d %~dp0talking_june\Avatar\june && color 0F && echo ========== JUNE VA ========== && python -m june_va --config config-enhanced-multilingual.json"
    timeout /t 4 /nobreak >nul
    echo [OK] June VA started
) else (
    echo [SKIP] June VA directory not found
)
echo.

REM 7. CBT Backend (Port 8002)
echo [7/7] Starting CBT Backend (Port 8002)...
if exist "%~dp0cbt-backend" (
    start "CBT Backend" cmd /k "cd /d %~dp0cbt-backend && color 0D && echo ========== CBT BACKEND (Port 8002) ========== && python app.py"
    timeout /t 4 /nobreak >nul
    echo [OK] CBT Backend started
) else (
    echo [SKIP] CBT Backend directory not found
)
echo.

REM ========================================================================
REM INITIALIZATION WAIT
REM ========================================================================

echo ========================================================================
echo                    ALL SERVICES STARTED!
echo ========================================================================
echo.
echo Waiting 20 seconds for all services to initialize...
timeout /t 20 /nobreak >nul

REM ========================================================================
REM OPEN BROWSER
REM ========================================================================

echo.
echo Opening browser to main application...
start http://localhost:3000
timeout /t 2 /nobreak >nul

REM ========================================================================
REM STATUS DISPLAY
REM ========================================================================

cls
echo.
echo ========================================================================
echo              SANJEEVANI - ALL MODULES RUNNING!
echo ========================================================================
echo.
echo [MAIN APPLICATION]
echo   http://localhost:3000
echo.
echo ========================================================================
echo [FRONTEND MODULES - Access via browser]
echo ========================================================================
echo.
echo   1. Homepage:              http://localhost:3000/
echo   2. Chatbot:               http://localhost:3000/chat
echo   3. Pharmacy Support:      http://localhost:3000/pharmacy-support
echo   4. Prescription Analysis: http://localhost:3000/prescription-analysis
echo   5. Sanjeevani Avatar:     http://localhost:3000/sanjeevani
echo   6. Outbreak Alerts:       http://localhost:3000/outbreak-alerts
echo   7. Community Forum:       http://localhost:3000/community-forum
echo   8. CBT Therapy:           http://localhost:3000/cbt
echo.
echo ========================================================================
echo [BACKEND SERVICES - Running in background]
echo ========================================================================
echo.
echo   - Backend API:            http://localhost:5000
echo   - OCR Service:            http://localhost:5001
echo   - CBT Backend:            http://localhost:8002
echo   - Avatar Bridge:          ws://localhost:8765
echo   - Audio Server:           http://localhost:8001
echo   - TalkingHead:            http://localhost:8080
echo.
echo ========================================================================
echo [SERVICE WINDOWS]
echo ========================================================================
echo.
echo   All services are running in separate command windows.
echo   Check each window for service logs and status.
echo   To stop all services, close this window or press Ctrl+C.
echo.
echo ========================================================================
echo.
echo                    READY FOR DEMO!
echo.
echo ========================================================================
echo.
pause
