@echo off
echo Starting Sanjeevani Chatbot...
echo.
echo Step 1: Checking Ollama...
echo Please make sure Ollama is running in another terminal with: ollama serve
echo.
echo Step 2: Starting Backend Server...
start cmd /k "cd backend && npm start"
timeout /t 3 /nobreak >nul
echo.
echo Step 3: Backend server started on http://localhost:5000
echo.
echo Step 4: Starting Frontend...
start cmd /k "npm run dev"
echo.
echo All services are starting! You can now use the chatbot.
echo.
pause
