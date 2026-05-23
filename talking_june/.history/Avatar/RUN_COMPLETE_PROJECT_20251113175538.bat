@echo off
REM ========================================================================
REM  JUNE VA + TALKINGHEAD - COMPLETE PROJECT STARTER
REM  Poora project ek click mein start ho jayega!
REM ========================================================================

setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo           JUNE VA + TALKINGHEAD - COMPLETE PROJECT STARTER
echo ========================================================================
echo.
echo  Yeh script automatically:
echo   1. Purane processes ko band karega
echo   2. Bridge Server start karega
echo   3. TalkingHead start karega  
echo   4. Browser khol dega
echo   5. June VA start karega (Enhanced Multilingual Mode)
echo.
echo ========================================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM =======================================================================
REM STEP 1: Clean up old processes
REM =======================================================================
echo [STEP 1/5] Purane processes ko band kar rahe hain...
echo.

REM Check and kill processes on required ports
set PORTS=8765 8001 8080

for %%P in (%PORTS%) do (
    echo Checking port %%P...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%P" ^| findstr "LISTENING"') do (
        echo   Port %%P par process mila (PID: %%a), band kar rahe hain...
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Wait for ports to be released
timeout /t 2 /nobreak >nul

echo.
echo ✅ Cleanup complete!
echo.

REM =======================================================================
REM STEP 2: Start Bridge Server
REM =======================================================================
echo ========================================================================
echo [STEP 2/5] Bridge Server start kar rahe hain...
echo ========================================================================
echo.

if not exist "bridge_server.py" (
    echo ❌ ERROR: bridge_server.py nahi mila!
    echo    Please check aap sahi directory mein hain.
    pause
    exit /b 1
)

start "June VA - Bridge Server" cmd /k "title June VA - Bridge Server && color 0A && python bridge_server.py"

echo ⏳ Bridge Server start ho raha hai...
timeout /t 3 /nobreak >nul
echo ✅ Bridge Server started on ws://localhost:8765
echo.

REM =======================================================================
REM STEP 3: Start TalkingHead
REM =======================================================================
echo ========================================================================
echo [STEP 3/5] TalkingHead Avatar start kar rahe hain...
echo ========================================================================
echo.

if not exist "TalkingHead" (
    echo ❌ ERROR: TalkingHead directory nahi mili!
    pause
    exit /b 1
)

start "TalkingHead - Avatar Server" cmd /k "title TalkingHead - Avatar Server && color 0B && cd TalkingHead && python -m http.server 8080"

echo ⏳ TalkingHead server start ho raha hai...
timeout /t 3 /nobreak >nul
echo ✅ TalkingHead started on http://localhost:8080
echo.

REM =======================================================================
REM STEP 4: Open Browser
REM =======================================================================
echo ========================================================================
echo [STEP 4/5] Browser khol rahe hain...
echo ========================================================================
echo.

timeout /t 2 /nobreak >nul
start http://localhost:8080

echo ✅ Browser opened: http://localhost:8080
echo.
echo ⏳ Browser mein TalkingHead load hone ka wait kar rahe hain...
timeout /t 3 /nobreak >nul
echo.

REM =======================================================================
REM STEP 5: Start June VA
REM =======================================================================
echo ========================================================================
echo [STEP 5/5] June VA start kar rahe hain (Enhanced Multilingual Mode)
echo ========================================================================
echo.

if not exist "june" (
    echo ❌ ERROR: june directory nahi mili!
    pause
    exit /b 1
)

REM Check which config to use
if exist "june\config-enhanced-multilingual.json" (
    set CONFIG_FILE=config-enhanced-multilingual.json
    echo ✨ Using ENHANCED configuration for maximum accuracy!
    echo    Features: Multi-pass detection, Smart voice selection, Hinglish support
) else if exist "june\config.json" (
    set CONFIG_FILE=config.json
    echo ℹ️  Using standard configuration
) else (
    echo ❌ ERROR: Config file nahi mila!
    echo    Please check june/config.json exists
    pause
    exit /b 1
)

echo.
echo Configuration: !CONFIG_FILE!
echo.

REM Set Google Cloud credentials if available
if exist "vaani-474822-49ec0963711e.json" (
    set GOOGLE_APPLICATION_CREDENTIALS=%~dp0vaani-474822-49ec0963711e.json
    echo ✅ Google Cloud credentials loaded
) else (
    echo ⚠️  Google Cloud credentials file not found (vaani-474822-49ec0963711e.json)
    echo    STT/TTS will try to use environment variable
)

echo.
echo ========================================================================
echo  ALL SERVICES ARE RUNNING!
echo ========================================================================
echo.
echo  ✅ Bridge Server:    ws://localhost:8765  (WebSocket)
echo  ✅ Audio Server:     http://localhost:8001 (Audio files)
echo  ✅ TalkingHead:      http://localhost:8080 (Avatar interface)
echo  ✅ June VA:          Starting... (Voice assistant)
echo.
echo ========================================================================
echo  HOW TO USE:
echo ========================================================================
echo.
echo  1. Browser mein TalkingHead avatar load hoga
echo  2. Console mein "Listening for sound..." dikhega
echo  3. Microphone mein bolo:
echo     - "Hey June, kaise ho?"
echo     - "मुझे help चाहिए"
echo     - "Can you help me?"
echo.
echo  4. Avatar automatically lip-sync karega!
echo.
echo  Press Ctrl+C to stop June VA
echo  (Other windows automatically band nahi honge - manually close karein)
echo.
echo ========================================================================
echo.

REM Start June VA in this terminal
cd june
python -m june_va --config !CONFIG_FILE!

REM If June VA exits, show exit message
echo.
echo ========================================================================
echo  JUNE VA STOPPED
echo ========================================================================
echo.
echo  June VA band ho gaya hai.
echo  
echo  Other services abhi bhi chal rahe hain:
echo    - Bridge Server window
echo    - TalkingHead window
echo.
echo  Unhe manually band karne ke liye windows close kar dein.
echo.
echo  Ya phir sab ek saath band karne ke liye:
echo    Press any key to close all services...
echo.
pause >nul

REM Kill all related processes
echo.
echo Sab services band kar rahe hain...
taskkill /FI "WindowTitle eq June VA - Bridge Server*" /T /F 2>nul
taskkill /FI "WindowTitle eq TalkingHead - Avatar Server*" /T /F 2>nul

echo.
echo ✅ All services stopped!
echo.
echo    Thank you for using June VA + TalkingHead!
echo    Phir milenge! 👋
echo.
timeout /t 3
exit /b 0
