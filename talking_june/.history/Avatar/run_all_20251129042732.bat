@echo off
REM Run all services for June VA + TalkingHead (double-click this file to start everything)

:: Change to repository root (directory containing this script)
cd /d "%~dp0"

:: Set Google credentials (update path if different)
set "GOOGLE_APPLICATION_CREDENTIALS=C:\Users\imahi\avatar_talking\Avatar\vaani-474822-49ec0963711e.json"

REM === Ollama must be running for LLM to work ===
REM Start Ollama manually if not running:
REM    ollama serve
REM Or double-click the Ollama app (Windows)

:: Run the smart startup script which opens separate windows for services
python smart_start.py

:: Keep the window open so you can see logs/errors
pause
