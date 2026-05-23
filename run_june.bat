@echo off
echo Starting June VA System...
echo.

echo Step 1: Starting Bridge Server...
start "Bridge Server" cmd /k "python talking_june/Avatar/bridge_server.py"
timeout /t 2 /nobreak >nul

echo Step 2: Starting June VA...
cd talking_june/Avatar/june
start "June VA" cmd /k "python -m june_va"
cd ../../..
timeout /t 2 /nobreak >nul

echo Step 3: Starting Frontend...
start "Frontend" cmd /k "npm run dev"

echo.
echo ✅ All June VA services started!
echo 1. Bridge Server (Port 8765/8001)
echo 2. June VA (Waiting for Sanjeevani)
echo 3. Frontend (http://localhost:5173)
echo.
echo 👉 Go to /sanjeevani to activate voice capture!
pause
