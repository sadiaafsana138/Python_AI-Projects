# 📓 NoteAgent

> Listens to browser videos → writes handwritten study notes in **English & বাংলা**. Works even when your speakers are muted. 🤫

Built with Groq Whisper (transcription) + LLaMA 3.3 70B (note generation). Completely free.

---

## ✨ Features

- 🎧 Captures audio directly from any browser tab — no microphone needed
- 🤫 Works even when your speakers are muted
- 📝 Generates structured handwritten-style notes every 30 seconds
- 🌐 Supports English, বাংলা, and 99+ other languages (auto-detected)
- 💾 Export notes as Markdown, HTML, or PDF
- 💰 100% free — Groq's free tier covers ~4 hours of lectures per day

---

## ⚙️ Setup *(one time)*

### 1. Get a free Groq API key
Go to [console.groq.com](https://console.groq.com) — no credit card needed. Copy your `gsk_...` key.

### 2. Add your API key
Create a `.env` file in the project folder:
```
GROQ_API_KEY=gsk_your_key_here
```

### 3. Run the app

**Windows:**
```
run.bat
```

**Mac/Linux:**
```bash
./run.sh
```

### 4. Open in browser
Go to **http://localhost:5000** in **Chrome or Edge** *(Firefox/Safari have limited tab audio support)*

---

## 🎬 Daily Use

1. Open **http://localhost:5000**
2. Paste your Groq key in the top bar *(saved automatically for next time)*
3. Pick language: 🌐 Auto · 🇬🇧 English · 🇧🇩 বাংলা
4. Click **▶ Start**
5. In the popup:
   - Choose **Chrome Tab** → pick the tab with your video
   - ✅ **Tick "Also share tab audio"** ← this is important!
6. Play your video — mute your speakers if you want, it still works 🤫
7. Notes appear every ~30 seconds in the notebook panel
8. Click **■ Stop** when done
9. Export with **↓ MD**, **↓ HTML**, or **↓ PDF**

---

## 🎛️ Buttons

| Button | What it does |
|---|---|
| ▶ Start | Begin listening and capturing audio |
| ■ Stop | Stop listening |
| ✕ Clear | Wipe all notes and transcript |
| ↓ MD | Download notes as Markdown |
| ↓ HTML | Download as printable handwritten page |
| ↓ PDF | Open print dialog to save as PDF |

---

## 🏗️ How It Works

```
Browser Tab Audio
      ↓
  MediaRecorder (30s chunks)
      ↓
  Flask /upload-audio
      ↓
  Groq Whisper large-v3  →  transcript
      ↓
  Groq LLaMA 3.3 70B    →  structured notes (JSON)
      ↓
  SSE stream → UI renders handwritten note cards
```

---

## 🐞 Troubleshooting

| Problem | Fix |
|---|---|
| No notes appearing | Tick **"Also share tab audio"** in the sharing dialog |
| "API key required" | Paste your `gsk_...` key in the top bar |
| Notes not showing for music/intros | Normal — filler audio is skipped intentionally |
| Bangla looks like boxes | Check your internet — fonts load from Google Fonts |
| Wrong tab shared | Click ■ Stop, then ▶ Start again and pick the right tab |
| urllib 403 error | Your network blocks Groq — the app uses `requests` to fix this |

---

## 📁 Project Structure

```
files/
├── app.py          # Flask backend — transcription + note generation
├── run.bat         # Windows launcher
├── run.sh          # Mac/Linux launcher
├── README.md
├── .env            # Your API key (never commit this!)
├── .gitignore
└── static/
    └── index.html  # Frontend UI
```

---

## 🔒 Security

- Never commit `.env` to GitHub — it contains your API key
- The `.gitignore` file excludes `.env` and `venv/` automatically

---

## 💰 Is It Really Free?

Yes. Groq's free tier includes:
- ~**4 hours** of Whisper transcription per day
- Generous LLaMA 3.3 70B usage
- No credit card required

More than enough for a full day of classes.

---

Happy studying! ✏️
