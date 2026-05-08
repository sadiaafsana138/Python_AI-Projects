@echo off
echo NoteAgent - Lecture Note-Taking (Browser Capture - Groq)
echo ============================================================

REM Create venv if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing dependencies (Flask only - no PyAudio needed)...
pip install --quiet --upgrade pip
pip install --quiet flask

echo.
echo Ready!
echo Open http://localhost:5000 in Chrome or Edge
echo Get a free Groq API key at https://console.groq.com
echo.

python app.py
pause
