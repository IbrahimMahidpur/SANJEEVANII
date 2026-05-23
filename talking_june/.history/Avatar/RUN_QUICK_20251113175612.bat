@echo off
REM Simple & Fast Project Starter - No fancy messages, just works!

cd /d "%~dp0"

REM Kill old processes silently
for %%P in (8765 8001 8080) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%P" ^| findstr "LISTENING" 2^>nul') do (
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Start services
start "Bridge" cmd /k "python bridge_server.py"
timeout /t 2 /nobreak >nul

start "Avatar" cmd /k "cd TalkingHead && python -m http.server 8080"
timeout /t 2 /nobreak >nul

start http://localhost:8080
timeout /t 3 /nobreak >nul

REM Set credentials if available
if exist "vaani-474822-49ec0963711e.json" (
    set GOOGLE_APPLICATION_CREDENTIALS=%~dp0vaani-474822-49ec0963711e.json
)

REM Choose config
if exist "june\config-enhanced-multilingual.json" (
    set CONFIG=config-enhanced-multilingual.json
) else (
    set CONFIG=config.json
)

REM Start June
echo Starting June VA...
cd june
python -m june_va --config !CONFIG!

REM Cleanup
taskkill /FI "WindowTitle eq Bridge*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Avatar*" /T /F >nul 2>&1
exit /b 0
