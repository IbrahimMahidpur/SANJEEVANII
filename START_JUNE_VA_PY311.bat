@echo off
echo ========================================================================
echo           STARTING JUNE VA WITH PYTHON 3.11
echo ========================================================================
echo.

cd /d c:\Users\imahi\gpt\talking_june\Avatar\june

echo Setting Google Cloud credentials...
set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json
echo ✅ Credentials set
echo.

echo Using Python 3.11.9...
"C:\Program Files\Python311\python.exe" --version
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

"C:\Program Files\Python311\python.exe" -m june_va --config config-enhanced-multilingual.json --verbose

echo.
echo ========================================================================
echo June VA exited with code: %ERRORLEVEL%
echo ========================================================================
echo.
pause
