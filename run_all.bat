@echo off
echo ===================================================
echo STARTING COMPLETE SANJEEVANI PROJECT
echo ===================================================

echo 1. Starting Main App (Frontend + Node Backend)...
start "Main App Launcher" cmd /c "call start.bat"

echo 2. Starting Avatar Services (June VA + TalkingHead)...
start "Avatar Launcher" cmd /c "call start_sanjeevani_backend.bat"

echo 3. Starting OCR Service (MediScribe)...
start "OCR Service" cmd /k "cd prescriptionAnalysis/MediScribe-OCR && python app.py"

echo.
echo All launchers started. Please check the new windows.
echo IMPORTANT: Ensure Ollama is running in a separate terminal (ollama serve)!
pause
