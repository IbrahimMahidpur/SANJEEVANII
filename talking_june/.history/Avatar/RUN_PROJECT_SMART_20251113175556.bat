@echo off
REM ========================================================================
REM  JUNE VA + TALKINGHEAD - SMART STARTER
REM  Intelligent startup with automatic testing and error handling
REM ========================================================================

setlocal enabledelayedexpansion

title June VA + TalkingHead - Smart Starter
color 0E

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║     JUNE VA + TALKINGHEAD - COMPLETE PROJECT STARTER             ║
echo ║                                                                    ║
echo ║     🗣️  Voice Assistant + 🎭 3D Avatar + 🌉 WebSocket Bridge      ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Change to project directory
cd /d "%~dp0"

REM =======================================================================
REM PRE-FLIGHT CHECKS
REM =======================================================================
echo ┌────────────────────────────────────────────────────────────────────┐
echo │ PRE-FLIGHT CHECKS                                                  │
echo └────────────────────────────────────────────────────────────────────┘
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nahi mila! Please install Python 3.8+ first.
    pause
    exit /b 1
)
echo ✅ Python installed

REM Check critical files
set FILES_OK=1
if not exist "bridge_server.py" (
    echo ❌ bridge_server.py nahi mila!
    set FILES_OK=0
)
if not exist "TalkingHead\index.html" (
    echo ❌ TalkingHead\index.html nahi mila!
    set FILES_OK=0
)
if not exist "june" (
    echo ❌ june directory nahi mili!
    set FILES_OK=0
)

if !FILES_OK!==0 (
    echo.
    echo ❌ ERROR: Required files missing!
    echo    Please check aap sahi directory mein hain.
    pause
    exit /b 1
)
echo ✅ All critical files found

REM Check for enhanced config
if exist "june\config-enhanced-multilingual.json" (
    echo ✅ Enhanced multilingual config available
    set USE_ENHANCED=1
) else (
    echo ℹ️  Using standard config
    set USE_ENHANCED=0
)

echo.

REM =======================================================================
REM OPTIONAL: Run Tests
REM =======================================================================
if exist "test_enhanced_multilingual.py" (
    echo ┌────────────────────────────────────────────────────────────────────┐
    echo │ OPTIONAL: TEST ENHANCED FEATURES                                  │
    echo └────────────────────────────────────────────────────────────────────┘
    echo.
    echo Enhanced multilingual test suite available.
    echo.
    choice /C YN /N /M "Run tests before starting? (Y/N): "
    if errorlevel 2 goto SKIP_TESTS
    if errorlevel 1 goto RUN_TESTS

    :RUN_TESTS
    echo.
    echo Running tests...
    python test_enhanced_multilingual.py
    if errorlevel 1 (
        echo.
        echo ⚠️  Some tests failed!
        choice /C YN /N /M "Continue anyway? (Y/N): "
        if errorlevel 2 (
            echo.
            echo Startup cancelled by user.
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo ✅ All tests passed!
    )
    echo.
    timeout /t 2 /nobreak >nul

    :SKIP_TESTS
)

REM =======================================================================
REM CLEANUP OLD PROCESSES
REM =======================================================================
echo ┌────────────────────────────────────────────────────────────────────┐
echo │ STEP 1/5: CLEANUP OLD PROCESSES                                   │
echo └────────────────────────────────────────────────────────────────────┘
echo.

set CLEANUP_NEEDED=0
for %%P in (8765 8001 8080) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%P" ^| findstr "LISTENING" 2^>nul') do (
        echo   🔍 Found process on port %%P (PID: %%a)
        taskkill /PID %%a /F >nul 2>&1
        set CLEANUP_NEEDED=1
    )
)

if !CLEANUP_NEEDED!==1 (
    echo   ✅ Old processes cleaned up
    timeout /t 2 /nobreak >nul
) else (
    echo   ✅ No cleanup needed - ports are free
)
echo.

REM =======================================================================
REM START BRIDGE SERVER
REM =======================================================================
echo ┌────────────────────────────────────────────────────────────────────┐
echo │ STEP 2/5: START BRIDGE SERVER                                     │
echo └────────────────────────────────────────────────────────────────────┘
echo.

start "🌉 June Bridge Server" cmd /k "title 🌉 June Bridge Server && color 0A && echo Starting Bridge Server... && python bridge_server.py"

echo   ⏳ Waiting for Bridge Server...
timeout /t 3 /nobreak >nul

REM Verify Bridge Server started
netstat -an | findstr ":8765" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   ⚠️  Bridge Server might not have started properly
    echo      Please check the Bridge Server window for errors
    pause
) else (
    echo   ✅ Bridge Server running on ws://localhost:8765
)
echo.

REM =======================================================================
REM START TALKINGHEAD
REM =======================================================================
echo ┌────────────────────────────────────────────────────────────────────┐
echo │ STEP 3/5: START TALKINGHEAD AVATAR                                │
echo └────────────────────────────────────────────────────────────────────┘
echo.

start "🎭 TalkingHead Avatar" cmd /k "title 🎭 TalkingHead Avatar && color 0B && echo Starting TalkingHead... && cd TalkingHead && python -m http.server 8080"

echo   ⏳ Waiting for TalkingHead...
timeout /t 3 /nobreak >nul

REM Verify TalkingHead started
netstat -an | findstr ":8080" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   ⚠️  TalkingHead might not have started properly
    echo      Please check the TalkingHead window for errors
    pause
) else (
    echo   ✅ TalkingHead running on http://localhost:8080
)
echo.

REM =======================================================================
REM OPEN BROWSER
REM =======================================================================
echo ┌────────────────────────────────────────────────────────────────────┐
echo │ STEP 4/5: OPEN BROWSER                                            │
echo └────────────────────────────────────────────────────────────────────┘
echo.

timeout /t 2 /nobreak >nul
start http://localhost:8080

echo   ✅ Browser opened: http://localhost:8080
echo   ⏳ Waiting for page to load...
timeout /t 4 /nobreak >nul
echo.

REM =======================================================================
REM START JUNE VA
REM =======================================================================
echo ┌────────────────────────────────────────────────────────────────────┐
echo │ STEP 5/5: START JUNE VA                                           │
echo └────────────────────────────────────────────────────────────────────┘
echo.

REM Determine config file
if !USE_ENHANCED!==1 (
    set CONFIG_FILE=config-enhanced-multilingual.json
    echo   ✨ Using ENHANCED MULTILINGUAL configuration
    echo.
    echo   Enhanced Features:
    echo     • Multi-pass language detection (Hindi/Bengali/English)
    echo     • Smart Hinglish processing
    echo     • Optimal voice selection per sentence
    echo     • Advanced text polishing
    echo     • Cultural awareness
) else (
    set CONFIG_FILE=config.json
    echo   ℹ️  Using STANDARD configuration
)

echo.

REM Set Google Cloud credentials
if exist "vaani-474822-49ec0963711e.json" (
    set GOOGLE_APPLICATION_CREDENTIALS=%~dp0vaani-474822-49ec0963711e.json
    echo   ✅ Google Cloud credentials set
) else (
    echo   ⚠️  Credentials file not found - using environment variable
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   ALL SERVICES READY! 🎉
echo ═══════════════════════════════════════════════════════════════════
echo.
echo   Services Running:
echo   ✅ Bridge Server:    ws://localhost:8765  (WebSocket)
echo   ✅ Audio Server:     http://localhost:8001 (Audio files)
echo   ✅ TalkingHead:      http://localhost:8080 (3D Avatar)
echo   ✅ June VA:          Starting now... (Voice Assistant)
echo.
echo ───────────────────────────────────────────────────────────────────
echo   HOW TO USE:
echo ───────────────────────────────────────────────────────────────────
echo.
echo   1. Browser mein TalkingHead avatar dikhega
echo   2. Wait for "Listening for sound..." message
echo   3. Speak into microphone:
echo      • "Hey June, kaise ho?"
echo      • "मुझे help चाहिए"
echo      • "Can you help me?"
echo      • "Explain machine learning"
echo.
echo   4. Avatar will automatically lip-sync! 🎭
echo.
echo ───────────────────────────────────────────────────────────────────
echo   CONTROLS:
echo ───────────────────────────────────────────────────────────────────
echo.
echo   • Press Ctrl+C to stop June VA
echo   • Type "exit" or "quit" to close gracefully
echo   • Close windows manually to stop other services
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.

REM Start June VA
cd june
python -m june_va --config !CONFIG_FILE!

REM =======================================================================
REM CLEANUP ON EXIT
REM =======================================================================
echo.
echo.
echo ═══════════════════════════════════════════════════════════════════
echo   JUNE VA STOPPED
echo ═══════════════════════════════════════════════════════════════════
echo.
echo   June VA has been closed.
echo.
echo   Other services are still running:
echo     • Bridge Server (WebSocket)
echo     • TalkingHead (Avatar)
echo.

choice /C YN /N /M "Close all services? (Y/N): "
if errorlevel 2 goto END
if errorlevel 1 goto CLEANUP

:CLEANUP
echo.
echo   Closing all services...
taskkill /FI "WindowTitle eq *June Bridge Server*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq *TalkingHead Avatar*" /T /F >nul 2>&1
timeout /t 1 /nobreak >nul
echo   ✅ All services stopped

:END
echo.
echo ═══════════════════════════════════════════════════════════════════
echo   Thank you for using June VA + TalkingHead! 🙏
echo   Phir milenge! 👋
echo ═══════════════════════════════════════════════════════════════════
echo.
timeout /t 3
exit /b 0
