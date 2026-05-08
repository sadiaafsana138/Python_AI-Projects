#!/bin/bash
# ─── NoteAgent · Lecture Note-Taking Setup & Run ──────────────────────────

echo "🎓 NoteAgent · Lecture Note-Taking (Browser Capture · Groq)"
echo "============================================================"

# Create venv if needed
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment…"
  python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

echo "📦 Installing dependencies (Flask only — no PyAudio needed)…"
pip install --quiet --upgrade pip
pip install --quiet flask

echo ""
echo "✅ Ready!"
echo "🌐 Open http://localhost:5000 in Chrome or Edge"
echo "🔑 Get a free Groq API key at https://console.groq.com"
echo ""

python app.py
