@echo off
echo ========================================
echo   MediScribe-OCR Application Starter
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

echo Starting Flask Backend Server...
echo Server will run on http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the Flask application
python app.py

pause
