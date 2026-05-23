@echo off
echo ========================================================================
echo     RESTARTING SANJEEVANI, CBT, AND PHARMACY SUPPORT MODULES
echo ========================================================================
echo.

REM Kill existing processes
echo [CLEANUP] Stopping all services...
taskkill /F /IM node.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul
echo Done.
echo.

REM 1. Start Backend API (needed for Pharmacy Support and Chatbot)
echo [1/6] Starting Backend API (Port 5000)...
start "Backend API" cmd /k "cd /d %~dp0backend && color 0E && echo ========== BACKEND API ========== && npm start"
timeout /t 5 /nobreak >nul

REM 2. Start Frontend (all modules)
echo [2/6] Starting Frontend (Port 3000)...
start "Frontend" cmd /k "cd /d %~dp0 && color 0B && echo ========== FRONTEND ========== && npm run dev"
timeout /t 5 /nobreak >nul

REM 3. Start Avatar Bridge (for Sanjeevani)
echo [3/6] Starting Avatar Bridge (Port 8765/8001)...
if exist "%~dp0talking_june\Avatar\bridge_server.py" (
    start "Avatar Bridge" cmd /k "cd /d %~dp0talking_june\Avatar && color 0A && echo ========== AVATAR BRIDGE ========== && python bridge_server.py"
    timeout /t 3 /nobreak >nul
)

REM 4. Start TalkingHead (for Sanjeevani)
echo [4/6] Starting TalkingHead (Port 8080)...
if exist "%~dp0talking_june\Avatar\TalkingHead" (
    start "TalkingHead" cmd /k "cd /d %~dp0talking_june\Avatar\TalkingHead && color 0C && echo ========== TALKINGHEAD ========== && python -m http.server 8080"
    timeout /t 3 /nobreak >nul
)

REM 5. Start June VA (for Sanjeevani)
echo [5/6] Starting June VA...
if exist "%~dp0talking_june\Avatar\june" (
    if exist "%~dp0vaani-474822-36de07e0981f.json" (
        set GOOGLE_APPLICATION_CREDENTIALS=%~dp0vaani-474822-36de07e0981f.json
    )
    start "June VA" cmd /k "cd /d %~dp0talking_june\Avatar\june && color 0F && echo ========== JUNE VA ========== && python -m june_va --config config-enhanced-multilingual.json"
    timeout /t 3 /nobreak >nul
)

REM 6. Start CBT Backend (Port 8002)
echo [6/6] Starting CBT Backend (Port 8002)...
start "CBT Backend" cmd /k "cd /d %~dp0cbt-backend && color 0D && echo ========== CBT BACKEND ========== && python app.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================================================
echo                    ALL SERVICES STARTED!
echo ========================================================================
echo.
echo Waiting 15 seconds for services to initialize...
timeout /t 15 /nobreak >nul
echo.
echo Opening browser...
start http://localhost:3000
echo.
echo ========================================================================
echo.
echo [SERVICES RUNNING]:
echo   - Frontend:        http://localhost:3000
echo   - Backend API:     http://localhost:5000
echo   - Avatar Bridge:   ws://localhost:8765
echo   - TalkingHead:     http://localhost:8080
echo   - CBT Backend:     http://localhost:8002
echo.
echo [MODULES TO TEST]:
echo   - Pharmacy Support:    http://localhost:3000/pharmacy-support
echo   - Sanjeevani Avatar:   http://localhost:3000/sanjeevani
echo   - CBT Module:          Backend ready on port 8002
echo.
echo ========================================================================
echo.
pause
