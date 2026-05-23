@echo off
echo Starting Sanjeevani Services...
echo.

REM Start Bridge Server
start "Sanjeevani - Bridge Server" cmd /k "cd /d c:\Users\imahi\gpt\talking_june\Avatar && color 0A && python bridge_server.py"
timeout /t 3 /nobreak >nul

REM Start TalkingHead
start "Sanjeevani - TalkingHead" cmd /k "cd /d c:\Users\imahi\gpt\talking_june\Avatar\TalkingHead && color 0C && python -m http.server 8080"
timeout /t 3 /nobreak >nul

REM Start June VA
cd /d c:\Users\imahi\gpt\talking_june\Avatar\june
set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json
start "Sanjeevani - June VA" cmd /k "cd /d c:\Users\imahi\gpt\talking_june\Avatar\june && set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json && color 0F && python -m june_va --config config-enhanced-multilingual.json"

echo.
echo ========================================
echo Sanjeevani Services Started!
echo ========================================
echo.
echo Bridge Server: ws://localhost:8765
echo TalkingHead: http://localhost:8080  
echo June VA: Running with multilingual support
echo.
echo Test Sanjeevani at: http://localhost:3000/sanjeevani
echo.
pause
