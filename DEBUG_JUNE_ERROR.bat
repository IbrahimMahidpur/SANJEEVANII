@echo off
cd /d c:\Users\imahi\gpt\talking_june\Avatar\june
set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json
python -m june_va --config config-enhanced-multilingual.json > output.log 2>&1
echo Exit code: %ERRORLEVEL% >> output.log
type output.log
pause
