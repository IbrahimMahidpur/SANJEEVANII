@echo off
echo ========================================================================
echo              PHARMACY SUPPORT MODULE LAUNCHER
echo ========================================================================
echo.
echo This script will start the Pharmacy Support module:
echo   - Backend API (Port 5000)
echo   - Frontend (Port 3000)
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
    echo    The chatbot features will not work without it.
    echo.
)

echo.
echo ========================================================================
echo Starting Services...
echo ========================================================================
echo.

REM Kill any existing processes on required ports
echo [CLEANUP] Stopping any existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✅ Cleanup complete
echo.

REM Start Backend (Node.js API)
echo [1/2] Starting Backend API Server...
start "Pharmacy Support - Backend API" cmd /k "cd /d %~dp0backend && color 0E && echo ========================================== && echo    BACKEND API SERVER && echo    Port: 5000 && echo ========================================== && echo. && npm start"
timeout /t 5 /nobreak >nul
echo ✅ Backend API started on http://localhost:5000
echo.

REM Start Frontend (React/Vite)
echo [2/2] Starting Frontend...
start "Pharmacy Support - Frontend" cmd /k "cd /d %~dp0 && color 0B && echo ========================================== && echo    FRONTEND (REACT/VITE) && echo    Port: 3000 && echo ========================================== && echo. && npm run dev"
timeout /t 5 /nobreak >nul
echo ✅ Frontend started on http://localhost:3000
echo.

echo ========================================================================
echo              PHARMACY SUPPORT MODULE STARTED!
echo ========================================================================
echo.
echo 🌐 ACCESS THE MODULE:
echo    http://localhost:3000/pharmacy-support
echo.
echo 📋 FEATURES AVAILABLE:
echo    ✅ Find Nearby Pharmacies and Hospitals
echo    ✅ Search for Medicine Availability
echo    ✅ Locate Doctors by Specialization
echo    ✅ Find Health Camps and Vaccination Centers
echo    ✅ AI Medical Chatbot
echo.
echo 🔧 BACKEND API:
echo    http://localhost:5000/api/pharmacy-support
echo.
echo ========================================================================
echo.
echo Opening Pharmacy Support module in browser...
timeout /t 5 /nobreak >nul
start http://localhost:3000/pharmacy-support
echo.
echo ========================================================================
echo.
echo ℹ️  NOTES:
echo    - Each service runs in its own colored window
echo    - Check individual windows for logs and errors
echo    - Press Ctrl+C in any window to stop that service
echo.
echo ========================================================================
echo.
echo Press any key to close this launcher window...
echo (Services will continue running in their own windows)
pause >nul
