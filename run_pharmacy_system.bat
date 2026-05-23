@echo off
echo ========================================================================
echo           STANDALONE PHARMACY SYSTEM LAUNCHER
echo ========================================================================
echo.
echo This script will start the standalone Pharmacy System:
echo   - Python FastAPI Backend (Port 8000)
echo   - React Frontend (Port 3000)
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
    echo    The AI chatbot features will not work without it.
    echo.
)

echo.
echo ========================================================================
echo Starting Services...
echo ========================================================================
echo.

REM Kill any existing processes on required ports
echo [CLEANUP] Stopping any existing services on ports 3000 and 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✅ Cleanup complete
echo.

REM Start Backend (Python FastAPI)
echo [1/2] Starting Python FastAPI Backend...
start "Pharmacy System - Backend API" cmd /k "cd /d %~dp0pharmacy-support\backend && color 0E && echo ========================================== && echo    PHARMACY SYSTEM - BACKEND API && echo    Port: 8000 && echo    Framework: FastAPI (Python) && echo ========================================== && echo. && python main.py"
timeout /t 5 /nobreak >nul
echo ✅ Backend API started on http://localhost:8000
echo.

REM Start Frontend (React)
echo [2/2] Starting React Frontend...
start "Pharmacy System - Frontend" cmd /k "cd /d %~dp0pharmacy-support\frontend && color 0B && echo ========================================== && echo    PHARMACY SYSTEM - FRONTEND && echo    Port: 3001 && echo    Framework: React && echo ========================================== && echo. && npm start"
timeout /t 5 /nobreak >nul
echo ✅ Frontend started on http://localhost:3001
echo.

echo ========================================================================
echo           STANDALONE PHARMACY SYSTEM STARTED!
echo ========================================================================
echo.
echo 🌐 ACCESS THE SYSTEM:
echo    http://localhost:3001
echo.
echo 📋 FEATURES AVAILABLE:
echo    ✅ Google Maps Integration - Find nearby pharmacies, hospitals, doctors
echo    ✅ Real Vaccine Data - CoWIN API integration
echo    ✅ AI Medical Chatbot - GPT-OSS 120B powered assistant
echo    ✅ Responsive Design - Works on all devices
echo.
echo 🔧 BACKEND API:
echo    http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 🔑 API ENDPOINTS:
echo    - Vaccine Centers: /api/v1/vaccine-centers
echo    - LLM Chat: /api/v1/llm
echo    - Health Check: /api/v1/health
echo.
echo ========================================================================
echo.
echo Opening Pharmacy System in browser...
timeout /t 8 /nobreak >nul
start http://localhost:3001
echo.
echo ========================================================================
echo.
echo ℹ️  NOTES:
echo    - Each service runs in its own colored window
echo    - Backend (Yellow): Python FastAPI on port 8000
echo    - Frontend (Cyan): React app on port 3000
echo    - Check individual windows for logs and errors
echo    - Press Ctrl+C in any window to stop that service
echo.
echo    📚 For API documentation, visit: http://localhost:8000/docs
echo.
echo ========================================================================
echo.
echo Press any key to close this launcher window...
echo (Services will continue running in their own windows)
pause >nul
