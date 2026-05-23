@echo off
echo ========================================================================
echo           SANJEEVANI SERVICES - STATUS CHECK
echo ========================================================================
echo.

echo Checking required ports...
echo.

REM Check each port
set ALL_RUNNING=1

echo [1/4] Bridge Server (port 8765)...
netstat -ano | findstr ":8765" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo       ✅ RUNNING
) else (
    echo       ❌ NOT RUNNING
    set ALL_RUNNING=0
)

echo [2/4] TalkingHead (port 8080)...
netstat -ano | findstr ":8080" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo       ✅ RUNNING
) else (
    echo       ❌ NOT RUNNING
    set ALL_RUNNING=0
)

echo [3/4] Audio Server (port 8001)...
netstat -ano | findstr ":8001" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo       ✅ RUNNING
) else (
    echo       ❌ NOT RUNNING
    set ALL_RUNNING=0
)

echo [4/4] Frontend (port 5173)...
netstat -ano | findstr ":5173" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo       ✅ RUNNING
) else (
    echo       ❌ NOT RUNNING
    set ALL_RUNNING=0
)

echo.
echo ========================================================================

if %ALL_RUNNING% equ 1 (
    echo  ✅ ALL SERVICES ARE RUNNING!
    echo.
    echo  You can now test Sanjeevani at:
    echo  http://localhost:5173
    echo.
    echo  Navigate to Sanjeevani module and click "Start Conversation"
) else (
    echo  ⚠️  SOME SERVICES ARE NOT RUNNING
    echo.
    echo  Please run: START_SANJEEVANI_COMPLETE.bat
)

echo ========================================================================
echo.
pause
