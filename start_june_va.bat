@echo off
echo ========================================================================
echo           STARTING JUNE VA (Voice Assistant)
echo ========================================================================
echo.

cd /d c:\Users\imahi\gpt\talking_june\Avatar\june

echo Setting Google Cloud credentials...
set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json
echo ✅ Credentials set
echo.

echo Checking Ollama model...
ollama list | findstr "gpt-oss:120b-cloud"
if %errorlevel% neq 0 (
    echo ❌ Model gpt-oss:120b-cloud not found!
    echo    Please run: ollama pull gpt-oss:120b-cloud
    pause
    exit /b 1
)
echo ✅ Model found
echo.

echo Starting June VA...
echo Configuration: config-enhanced-multilingual.json
echo Model: gpt-oss:120b-cloud
echo.
echo ========================================================================
echo  June VA will start listening after connecting to bridge server
echo  You should see: "⏸️  Starting in PAUSED state"
echo ========================================================================
echo.

python -m june_va --config config-enhanced-multilingual.json --verbose

echo.
echo ========================================================================
echo June VA exited with code: %ERRORLEVEL%
echo ========================================================================
echo.
pause
