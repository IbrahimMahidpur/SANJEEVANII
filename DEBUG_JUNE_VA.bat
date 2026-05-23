@echo off
title June VA Debug
color 0F
cd /d c:\Users\imahi\gpt\talking_june\Avatar\june
set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json
echo.
echo ========== JUNE VA DEBUG MODE ==========
echo.
echo Current Directory: %CD%
echo Google Credentials: %GOOGLE_APPLICATION_CREDENTIALS%
echo.
echo Checking Python...
python --version
echo.
echo Checking if june_va module exists...
python -c "import june_va; print('june_va module found')" 2>&1
echo.
echo Starting June VA...
echo.
python -m june_va --config config-enhanced-multilingual.json 2>&1
echo.
echo.
echo ========== JUNE VA EXITED ==========
echo Check errors above
echo.
pause
