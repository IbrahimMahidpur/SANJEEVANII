@echo off
echo ========================================
echo Starting All Sanjeevani Services
echo ========================================
echo.

REM Start Backend
echo [1/3] Starting Backend Server...
start "Sanjeevani Backend" cmd /k "cd /d %~dp0backend && npm start"
timeout /t 3 /nobreak >nul

REM Start Frontend
echo [2/3] Starting Frontend...
start "Sanjeevani Frontend" cmd /k "cd /d %~dp0 && npm run dev"
timeout /t 3 /nobreak >nul

REM Start OCR Service
echo [3/3] Starting OCR Service...
start "OCR Service" cmd /k "cd /d %~dp0prescriptionAnalysis\MediScribe-OCR && python app.py"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Services:
echo   - Frontend: http://localhost:3000
echo   - Backend:  http://localhost:5000
echo   - OCR:      http://localhost:5001
echo.
echo Opening browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul
