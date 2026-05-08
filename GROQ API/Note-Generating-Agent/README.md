# 📓 NoteAgent

> Listens to any browser tab → shows live subtitles → writes short smart study notes in **English & বাংলা** 🎓

Built with **Groq Whisper** (transcription) + **LLaMA 3.3 70B** (note generation). Completely free.

---

## ✨ Features

- 🎧 Captures audio from any browser tab — no microphone needed
- 📺 **Live subtitles** — transcript updates every ~7 seconds like real captions
- 📝 **Smart short notes** — accumulates ~28s of speech, then extracts only key points
- 🌐 **Auto language detection** — supports English, বাংলা, and 99+ languages
- 🔀 Works with **Banglish** (mixed Bangla + English) content naturally
- 🤫 Works even when your speakers are muted
- 💾 Export notes as **Markdown**, **HTML**, or **PDF**
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

### 3. Install dependencies & run

**Windows:**
```
run.bat
```

**Mac/Linux:**
```bash
./run.sh
```

### 4. Open in browser
Go to **http://localhost:5000** in **Chrome or Edge**
*(Firefox/Safari don't support tab audio sharing)*

---

## 🎬 Daily Use

1. Open **http://localhost:5000** in Chrome or Edge
2. Paste your Groq key in the top bar *(saved automatically)*
3. Pick language: 🌐 Auto · 🇬🇧 English · 🇧🇩 বাংলা
4. Click **▶ Start**
5. In the popup:
   - Choose **Chrome Tab** → pick the tab with your video
   - ✅ **Tick "Also share tab audio"** ← important!
6. Play your video — mute your speakers if needed, it still works 🤫
7. **Live transcript** appears on the right every ~7 seconds
8. **Notes** appear on the left every ~28 seconds (key points only)
9. Click **■ Stop** when done — remaining buffer is saved as a final note
10. Export with **↓ MD**, **↓ HTML**, or **↓ PDF**

---

## 🎛️ Buttons

| Button | What it does |
|---|---|
| ▶ Start | Begin listening and capturing audio |
| ■ Stop | Stop and flush any remaining notes |
| ✕ Clear | Wipe all notes and transcript |
| ↓ MD | Download notes as Markdown |
| ↓ HTML | Download as printable handwritten page |
| ↓ PDF | Open print dialog to save as PDF |

---

## 🏗️ How It Works

```
Browser Tab Audio
      ↓
  MediaRecorder (~7s chunks)
      ↓
  Flask /upload-audio
      ↓
  Groq Whisper large-v3  →  live transcript (subtitle speed)
      ↓
  Buffer 4 chunks (~28s)
      ↓
  Groq LLaMA 3.3 70B    →  short smart notes (max 3 bullets)
      ↓
  SSE stream → UI renders handwritten note cards
```

---

## 🌐 Language Support

| Mode | Behavior |
|---|---|
| 🌐 Auto | Whisper detects language automatically |
| 🇬🇧 English | Forces English transcription |
| 🇧🇩 বাংলা | Forces Bangla transcription (best for Bangla videos) |

For **Banglish** content (Bangla sentences with English technical terms), use 🌐 Auto — notes will naturally mix both languages.

---

## 📁 Project Structure

```
NoteAgent/
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

## 🐞 Troubleshooting

| Problem | Fix |
|---|---|
| No transcript appearing | Tick **"Also share tab audio"** in the sharing popup |
| Notes not appearing | Wait ~28s (4 chunks needed before first note) |
| Music/intro skipped | Normal — filler audio is intentionally skipped |
| Bangla looks like boxes | Check internet — fonts load from Google Fonts |
| Wrong tab shared | Click ■ Stop → ▶ Start again, pick correct tab |
| Can't hear audio | Check `suppressLocalAudioPlayback: false` in index.html |

---

## 🔒 Security

- Never commit `.env` to GitHub — it contains your API key
- `.gitignore` excludes `.env` and `venv/` automatically

---

## 💰 Is It Really Free?

Yes. Groq's free tier includes:
- ~**4 hours** of Whisper transcription per day
- Generous LLaMA 3.3 70B token allowance
- No credit card required

More than enough for a full day of classes. 🎓

---

Happy studying! ✏️
