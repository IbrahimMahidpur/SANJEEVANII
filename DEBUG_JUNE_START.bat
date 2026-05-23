@echo off
echo Starting June VA with error output...
echo.

cd /d c:\Users\imahi\gpt\talking_june\Avatar\june

set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json

echo Running: python -m june_va --config config-enhanced-multilingual.json
echo.

python -m june_va --config config-enhanced-multilingual.json

echo.
echo June VA exited with code: %ERRORLEVEL%
echo.
pause
