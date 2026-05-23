@echo off
title June VA - Voice Assistant
color 0F
cd /d c:\Users\imahi\gpt\talking_june\Avatar\june
set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\imahi\gpt\vaani-474822-36de07e0981f.json
echo.
echo ========== JUNE VA - VOICE ASSISTANT ==========
echo.
echo Starting June VA with Enhanced Multilingual Config...
echo Google Cloud Credentials: %GOOGLE_APPLICATION_CREDENTIALS%
echo.
python -m june_va --config config-enhanced-multilingual.json
echo.
echo June VA stopped.
pause
