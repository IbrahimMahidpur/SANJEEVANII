@echo off
echo ========================================================================
echo           RESTARTING ALL SANJEEVANI SERVICES
echo ========================================================================
echo.

REM Kill old processes
echo Stopping old services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start Bridge Server
echo [1/3] Starting Bridge Server...
cd /d c:\Users\imahi\gpt\talking_june\Avatar
start "Sanjeevani - Bridge Server" cmd /k "title Sanjeevani - Bridge Server && color 0A && python bridge_server.py"
timeout /t 3 /nobreak >nul
echo ✅ Bridge Server started
echo.

REM Start TalkingHead
echo [2/3] Starting TalkingHead...
start "Sanjeevani - TalkingHead" cmd /k "title Sanjeevani - TalkingHead && color 0B && cd TalkingHead && python -m http.server 8080"
timeout /t 3 /nobreak >nul
echo ✅ TalkingHead started
echo.

REM Start June VA with Python 3.11
echo [3/3] Starting June VA (Python 3.11)...
cd /d c:\Users\imahi\gpt\talking_june\Avatar\june
start "Sanjeevani - June VA" cmd /k "title Sanjeevani - June VA && color 0F && set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json && \"C:\Program Files\Python311\python.exe\" -m june_va --config config-enhanced-multilingual.json --verbose"
timeout /t 3 /nobreak >nul
echo ✅ June VA started
echo.

echo ========================================================================
echo  ✅ ALL BACKEND SERVICES RESTARTED!
echo ========================================================================
echo.
echo  Now refresh your browser: http://localhost:3000/sanjeevani
echo.
echo  The "Connecting..." should change to "Start Conversation"
echo.
pause
