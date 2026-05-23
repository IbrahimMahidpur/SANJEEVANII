@echo off
REM Start June VA with Enhanced Multilingual Configuration
REM Optimized for Hindi, English, and Hinglish

echo.
echo ========================================================================
echo  JUNE VA - ENHANCED MULTILINGUAL MODE
echo  Maximum Accuracy for Hindi, English, and Hinglish
echo ========================================================================
echo.

REM Check if we're in the right directory
if not exist "june\config-enhanced-multilingual.json" (
    echo ERROR: config-enhanced-multilingual.json not found!
    echo Please run this from the Avatar directory.
    pause
    exit /b 1
)

REM Test enhanced features first
echo [1/3] Testing enhanced multilingual features...
echo.
python test_enhanced_multilingual.py
if errorlevel 1 (
    echo.
    echo WARNING: Some tests failed. Continue anyway? (Y/N)
    choice /C YN /N
    if errorlevel 2 exit /b 1
)

echo.
echo ========================================================================
echo [2/3] Starting Bridge Server...
echo ========================================================================
echo.
start "Bridge Server" cmd /k "python bridge_server.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================================================
echo [3/3] Starting TalkingHead...
echo ========================================================================
echo.
start "TalkingHead" cmd /k "cd TalkingHead && python -m http.server 8080"
timeout /t 2 /nobreak >nul

REM Open browser
start http://localhost:8080

echo.
echo ========================================================================
echo  ALL SERVICES STARTED!
echo ========================================================================
echo.
echo  Bridge Server:  ws://localhost:8765  (WebSocket)
echo  Audio Server:   http://localhost:8001  (Audio files)
echo  TalkingHead:    http://localhost:8080  (Avatar interface)
echo.
echo  Now starting June VA with ENHANCED MULTILINGUAL config...
echo.
echo  Features:
echo   - Multi-pass language detection (Hindi/Bengali/English)
echo   - Smart Hinglish processing
echo   - Optimal voice selection per sentence
echo   - Advanced text polishing for natural TTS
echo.
echo ========================================================================
echo.

REM Wait a moment for services to be ready
timeout /t 3 /nobreak >nul

REM Start June VA with enhanced config
cd june
python -m june_va --config config-enhanced-multilingual.json

REM If June exits, close other windows
echo.
echo Shutting down other services...
taskkill /FI "WindowTitle eq Bridge Server*" /T /F 2>nul
taskkill /FI "WindowTitle eq TalkingHead*" /T /F 2>nul

echo.
echo Goodbye!
pause
