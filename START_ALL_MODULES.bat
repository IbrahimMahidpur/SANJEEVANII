@echo off
echo ========================================================================
echo              STARTING ALL SANJEEVANI SERVICES
echo ========================================================================
echo.

REM Kill any existing processes
echo [CLEANUP] Stopping existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8765" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8002" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo Done.
echo.

REM 1. Backend API
echo [1/7] Starting Backend API (Port 5000)...
start "Backend API" cmd /k "cd /d %~dp0backend && color 0E && npm start"
timeout /t 3 /nobreak >nul

REM 2. Frontend
echo [2/7] Starting Frontend (Port 3000)...
start "Frontend" cmd /k "cd /d %~dp0 && color 0B && npm run dev"
timeout /t 3 /nobreak >nul

REM 3. OCR Service
echo [3/7] Starting OCR Service (Port 5001)...
start "OCR Service" cmd /k "cd /d %~dp0prescriptionAnalysis\MediScribe-OCR && color 0D && python app.py"
timeout /t 3 /nobreak >nul

REM 4. Avatar Bridge
echo [4/7] Starting Avatar Bridge (Port 8765/8001)...
if exist "%~dp0talking_june\Avatar\bridge_server.py" (
    start "Avatar Bridge" cmd /k "cd /d %~dp0talking_june\Avatar && color 0A && python bridge_server.py"
    timeout /t 3 /nobreak >nul
) else (
    echo [SKIP] Avatar Bridge not found
)

REM 5. TalkingHead
echo [5/7] Starting TalkingHead (Port 8080)...
if exist "%~dp0talking_june\Avatar\TalkingHead" (
    start "TalkingHead" cmd /k "cd /d %~dp0talking_june\Avatar\TalkingHead && color 0C && python -m http.server 8080"
    timeout /t 3 /nobreak >nul
) else (
    echo [SKIP] TalkingHead not found
)

REM 6. June VA
echo [6/7] Starting June VA...
if exist "%~dp0talking_june\Avatar\june" (
    if exist "%~dp0vaani-474822-36de07e0981f.json" (
        set GOOGLE_APPLICATION_CREDENTIALS=%~dp0vaani-474822-36de07e0981f.json
    )
    start "June VA" cmd /k "cd /d %~dp0talking_june\Avatar\june && color 0F && python -m june_va --config config-enhanced-multilingual.json"
    timeout /t 3 /nobreak >nul
) else (
    echo [SKIP] June VA not found
)

REM 7. CBT Backend
echo [7/7] Starting CBT Backend (Port 8002)...
start "CBT Backend" cmd /k "cd /d %~dp0cbt-backend && color 0D && python app.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================================================
echo              ALL SERVICES STARTED!
echo ========================================================================
echo.
echo Waiting 15 seconds for services to initialize...
timeout /t 15 /nobreak >nul
echo.
echo Opening browser...
start http://localhost:3000
echo.
echo ========================================================================
echo                    SANJEEVANI IS NOW RUNNING!
echo ========================================================================
echo.
echo [MAIN APP]        http://localhost:3000
echo.
echo Press any key to close this launcher...
pause >nul
