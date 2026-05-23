@echo off
cd cbt-backend
echo Installing requirements...
pip install -r requirements.txt
echo Starting CBT Backend...
python app.py
pause
