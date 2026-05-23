@echo off
echo ========================================
echo Starting Sanjeevani Backend Services
echo ========================================
echo.

REM Change to the Avatar directory
cd /d "%~dp0talking_june\Avatar"

echo Starting all backend services...
echo This will open 3 windows:
echo   1. Bridge Server (WebSocket + HTTP)
echo   2. TalkingHead Frontend
echo   3. June VA Voice Assistant
echo.

REM Run the complete project batch file
call RUN_COMPLETE_PROJECT.bat

echo.
echo ========================================
echo Backend services started!
echo ========================================
echo.
echo Now you can:
echo 1. Go to http://localhost:3000 (or your React dev server)
echo 2. Click on Sanjeevani in the menu
echo 3. Start talking to the Avatar!
echo.
pause
