@echo off
echo ========================================================================
echo           RESTARTING SANJEEVANI MODULE
echo ========================================================================
echo.
echo Step 1: Stopping all running services...
echo.

REM Kill all processes on Sanjeevani ports
set PORTS=8765 8001 8080 3000 3001 5173

for %%P in (%PORTS%) do (
    echo Stopping services on port %%P...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%P" ^| findstr "LISTENING"') do (
        echo   Killing process PID: %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Also kill by window title
echo.
echo Stopping Sanjeevani windows by title...
taskkill /FI "WindowTitle eq *Sanjeevani*" /F /T >nul 2>&1
taskkill /FI "WindowTitle eq *June VA*" /F /T >nul 2>&1
taskkill /FI "WindowTitle eq *TalkingHead*" /F /T >nul 2>&1
taskkill /FI "WindowTitle eq *Bridge Server*" /F /T >nul 2>&1

REM Kill any Python processes related to bridge_server or june_va
echo Stopping Python processes...
taskkill /IM python.exe /F >nul 2>&1

REM Kill any Node processes (frontend)
echo Stopping Node processes...
taskkill /IM node.exe /F >nul 2>&1

echo.
echo ✅ All services stopped!
echo.
echo Waiting 3 seconds for ports to be released...
timeout /t 3 /nobreak >nul

echo.
echo ========================================================================
echo Step 2: Starting all services fresh...
echo ========================================================================
echo.

REM Change to Avatar directory
cd /d "%~dp0talking_june\Avatar"

REM Start Bridge Server
echo [1/4] Starting Bridge Server...
start "Sanjeevani - Bridge Server" cmd /k "title Sanjeevani - Bridge Server && color 0A && python bridge_server.py"
timeout /t 3 /nobreak >nul
echo ✅ Bridge Server started
echo.

REM Start TalkingHead
echo [2/4] Starting TalkingHead Avatar...
start "Sanjeevani - TalkingHead" cmd /k "title Sanjeevani - TalkingHead && color 0B && cd TalkingHead && python -m http.server 8080"
timeout /t 3 /nobreak >nul
echo ✅ TalkingHead started
echo.

REM Start June VA
echo [3/4] Starting June VA...
cd june

REM Set Google Cloud credentials
set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json

REM Determine config file
if exist "config-enhanced-multilingual.json" (
    set CONFIG_FILE=config-enhanced-multilingual.json
) else (
    set CONFIG_FILE=config.json
)

start "Sanjeevani - June VA" cmd /k "title Sanjeevani - June VA && color 0F && set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json && python -m june_va --config %CONFIG_FILE%"
timeout /t 3 /nobreak >nul
echo ✅ June VA started
echo.

REM Start Frontend
echo [4/4] Starting React Frontend...
cd /d "%~dp0"
start "Sanjeevani - Frontend" cmd /k "title Sanjeevani - Frontend && color 0E && npm run dev"
timeout /t 5 /nobreak >nul
echo ✅ Frontend starting...
echo.

echo ========================================================================
echo           ✅ SANJEEVANI MODULE RESTARTED!
echo ========================================================================
echo.
echo  All services are now running:
echo   ✅ Bridge Server:    ws://localhost:8765
echo   ✅ TalkingHead:      http://localhost:8080
echo   ✅ June VA:          Running
echo   ✅ Frontend:         http://localhost:3001 (or 5173)
echo.
echo  Opening browser...
echo.
timeout /t 3 /nobreak >nul

start http://localhost:3001

echo.
echo  Browser opened! Navigate to Sanjeevani module.
echo.
echo  Press any key to close this window...
pause >nul
