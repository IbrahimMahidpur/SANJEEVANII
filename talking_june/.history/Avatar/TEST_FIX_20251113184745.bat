@echo off
REM Quick Test Script for Audio & Lip-Sync Fix
REM जल्दी टेस्ट करने के लिए स्क्रिप्ट

echo ========================================
echo Audio & Lip-Sync Fix Test
echo ========================================
echo.

echo Step 1: Stopping all Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo Step 2: Cleaning ports...
for %%P in (8765 8001 8080) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%P" ^| findstr "LISTENING" 2^>nul') do (
        taskkill /PID %%a /F >nul 2>&1
    )
)
timeout /t 1 /nobreak >nul

echo Step 3: Starting Bridge Server...
start "Bridge" cmd /k "cd /d %~dp0 && python bridge_server.py"
timeout /t 3 /nobreak >nul

echo Step 4: Starting TalkingHead...
start "TalkingHead" cmd /k "cd /d %~dp0TalkingHead && python -m http.server 8080"
timeout /t 3 /nobreak >nul

echo Step 5: Opening browser...
start http://localhost:8080
timeout /t 3 /nobreak >nul

echo Step 6: Starting June VA with enhanced config...
cd /d %~dp0june
set GOOGLE_APPLICATION_CREDENTIALS=%~dp0vaani-474822-49ec0963711e.json

echo.
echo ========================================
echo IMPORTANT INSTRUCTIONS:
echo ========================================
echo 1. Click the AVATAR once to activate audio
echo 2. Open DevTools (F12) ^> Console tab
echo 3. Look for: [June Bridge] ✅ Connected
echo 4. Speak to June VA
echo 5. Check console for:
echo    - ✅ head.speakAudio completed with lip-sync
echo    - NO duplicate warnings
echo    - NO fallback messages
echo.
echo Starting June VA...
echo.

python -m june_va --config config-enhanced-multilingual.json

pause
