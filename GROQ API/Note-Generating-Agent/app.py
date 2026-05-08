"""
Lecture Note-Taking Agent (Browser-Capture Edition)
─────────────────────────────────────────────────────
- Captures TAB AUDIO from the browser (works even when video is muted on speakers)
- Transcribes with Groq Whisper Large v3 — subtitle speed (~7s chunks)
- Accumulates transcript and generates concise notes every ~4 chunks (~28s)
- Generates handwritten-style structured notes via Groq LLaMA 3.3 70B
- Live UI streamed over SSE at http://localhost:5000
- Free API key: https://console.groq.com
"""

import os
import json
import time
import threading
import tempfile
import requests
from collections import deque
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, Response, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

# ── State ────────────────────────────────────────────────────────────────────
state = {
    "recording": False,
    "transcript_chunks": [],   # list of {text, lang, ts}
    "notes": [],               # list of note dicts
    "status": "idle",
    "language": "auto",        # auto | en | bn
    "error": None,
}
sse_clients: list[deque] = []
lock = threading.Lock()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ── Note buffering — accumulate N transcript chunks before generating notes ──
NOTE_EVERY_N_CHUNKS = 4          # generate a note every ~4 transcripts (~28s)
_transcript_buffer: list[str] = []
_chunk_counter = 0

# ── SSE broadcast ────────────────────────────────────────────────────────────
def broadcast(event_type: str, data: dict):
    msg = f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    for q in list(sse_clients):
        try:
            q.append(msg)
        except Exception:
            if q in sse_clients:
                sse_clients.remove(q)

# ── Groq Notes (LLaMA 3.3 70B) ───────────────────────────────────────────────
def call_groq_notes(transcript_chunk: str, detected_lang: str) -> dict | None:
    if not GROQ_API_KEY:
        return None

    lang_instruction = {
        "bn": "The transcript is in Bangla (বাংলা). Write the notes in Bangla.",
        "en": "The transcript is in English. Write the notes in English.",
    }.get(detected_lang,
          "Write the notes in the same language as the transcript. "
          "If the transcript mixes Bangla and English, you may mix them too.")

    system_prompt = f"""You are a smart lecture assistant that extracts only the most important points.
{lang_instruction}

Given a transcript, extract ONLY the key important points — ignore filler, examples, and repetition.
Return ONLY valid JSON (no markdown fences, no commentary) in this exact schema:
{{
  "topic": "very short topic title (max 5 words)",
  "bullets": ["important point 1", "important point 2", "important point 3"],
  "summary": "one sentence summary",
  "keywords": ["term1", "term2"]
}}

Rules:
- Maximum 3 bullets — only the most important points
- Each bullet must be SHORT (max 12 words) and self-contained
- Skip examples, stories, and repeated ideas
- Keywords: only technical terms, formulas, names, or key concepts
- If there is nothing important (music, silence, filler talk), return: {{"skip": true}}"""

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 400,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Transcript:\n{transcript_chunk}"}
                ]
            },
            timeout=45
        )
        resp.raise_for_status()
        body = resp.json()
        text = body["choices"][0]["message"]["content"].strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        return json.loads(text)
    except Exception as e:
        print(f"[Groq notes error] {e}")
        return None

# ── Groq Whisper transcription ────────────────────────────────────────────────
def transcribe_audio(audio_path: str, language_hint: str = "auto") -> tuple[str, str]:
    """Returns (transcript_text, detected_language_code)."""
    if not GROQ_API_KEY:
        return "[No API key set]", ""

    try:
        ext = os.path.splitext(audio_path)[1].lstrip(".") or "webm"
        mime = {"webm": "audio/webm", "ogg": "audio/ogg", "wav": "audio/wav",
                "mp3": "audio/mpeg", "m4a": "audio/mp4"}.get(ext, "audio/webm")

        with open(audio_path, "rb") as f:
            files = {"file": (f"audio.{ext}", f, mime)}
            data = {
                "model": "whisper-large-v3",
                "response_format": "verbose_json",
            }
            if language_hint and language_hint != "auto":
                data["language"] = language_hint

            resp = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                files=files,
                data=data,
                timeout=90
            )
        resp.raise_for_status()
        result = resp.json()
        text = (result.get("text") or "").strip()
        lang = result.get("language", "") or ""
        return text, lang
    except Exception as e:
        print(f"[Groq Whisper error] {e}")
        return f"[Transcription error: {e}]", ""

# ── Background processing ─────────────────────────────────────────────────────
def process_chunk_async(audio_path: str, language_hint: str):
    global _transcript_buffer, _chunk_counter

    try:
        with lock:
            state["status"] = "processing"
        broadcast("status", {"status": "processing", "message": "⚙ Transcribing…"})

        text, detected_lang = transcribe_audio(audio_path, language_hint)

        try:
            os.unlink(audio_path)
        except OSError:
            pass

        if not text or text.startswith("["):
            with lock:
                state["status"] = "recording" if state["recording"] else "idle"
            broadcast("status", {
                "status": state["status"],
                "message": "🎙 Listening…" if state["recording"] else "⏹ Idle"
            })
            return

        # ── Stream transcript immediately (subtitle feel) ──────────────────
        chunk_record = {"text": text, "lang": detected_lang, "ts": time.time()}
        with lock:
            state["transcript_chunks"].append(chunk_record)
        broadcast("transcript", chunk_record)

        # ── Buffer transcript for note generation ──────────────────────────
        _transcript_buffer.append(text)
        _chunk_counter += 1

        # Generate notes every N chunks
        if _chunk_counter >= NOTE_EVERY_N_CHUNKS:
            broadcast("status", {"status": "processing", "message": "🧠 Writing notes…"})
            combined = " ".join(_transcript_buffer)
            _transcript_buffer = []
            _chunk_counter = 0

            note = call_groq_notes(combined, detected_lang)
            if note and not note.get("skip"):
                note["lang"] = detected_lang
                with lock:
                    state["notes"].append(note)
                broadcast("note", note)

        with lock:
            state["status"] = "recording" if state["recording"] else "idle"
        broadcast("status", {
            "status": state["status"],
            "message": "🎙 Listening…" if state["recording"] else "⏹ Idle"
        })
    except Exception as e:
        print(f"[process_chunk error] {e}")
        broadcast("error", {"message": f"Processing failed: {e}"})

# ── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/events")
def events():
    client_queue: deque = deque()
    sse_clients.append(client_queue)

    def generate():
        yield f"event: init\ndata: {json.dumps(state, ensure_ascii=False)}\n\n"
        try:
            while True:
                if client_queue:
                    yield client_queue.popleft()
                else:
                    yield ": keepalive\n\n"
                    time.sleep(15)
        except GeneratorExit:
            if client_queue in sse_clients:
                sse_clients.remove(client_queue)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@app.route("/start", methods=["POST"])
def start():
    global _transcript_buffer, _chunk_counter, GROQ_API_KEY
    data = request.get_json(silent=True) or {}
    key = (data.get("api_key") or "").strip()
    language = (data.get("language") or "auto").strip()
    if key and key.startswith("gsk_"):
        GROQ_API_KEY = key
    if not GROQ_API_KEY:
        return jsonify({"ok": False, "message": "Groq API key required"})
    with lock:
        state["recording"] = True
        state["status"] = "recording"
        state["language"] = language if language in ("auto", "en", "bn") else "auto"
        state["error"] = None
    _transcript_buffer = []
    _chunk_counter = 0
    broadcast("status", {"status": "recording", "message": "🎙 Listening…"})
    return jsonify({"ok": True})

@app.route("/stop", methods=["POST"])
def stop():
    global _transcript_buffer, _chunk_counter
    # Flush remaining buffer into a note if there's enough content
    if _transcript_buffer:
        combined = " ".join(_transcript_buffer)
        _transcript_buffer = []
        _chunk_counter = 0
        if len(combined.split()) > 10:
            threading.Thread(
                target=lambda: _flush_note(combined),
                daemon=True
            ).start()
    with lock:
        state["recording"] = False
        state["status"] = "idle"
    broadcast("status", {"status": "idle", "message": "⏹ Stopped"})
    return jsonify({"ok": True})

def _flush_note(text: str):
    """Generate a note from remaining buffered transcript on stop."""
    note = call_groq_notes(text, state.get("language", "auto"))
    if note and not note.get("skip"):
        note["lang"] = state.get("language", "")
        with lock:
            state["notes"].append(note)
        broadcast("note", note)

@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    if not state["recording"]:
        return jsonify({"ok": False, "message": "Not recording"}), 400
    if "audio" not in request.files:
        return jsonify({"ok": False, "message": "No audio file"}), 400

    f = request.files["audio"]
    mime = (f.mimetype or "audio/webm").lower()
    ext = "webm"
    if "ogg" in mime: ext = "ogg"
    elif "wav" in mime: ext = "wav"
    elif "mpeg" in mime or "mp3" in mime: ext = "mp3"
    elif "mp4" in mime or "m4a" in mime: ext = "m4a"

    tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
    f.save(tmp.name)
    tmp.close()

    threading.Thread(
        target=process_chunk_async,
        args=(tmp.name, state["language"]),
        daemon=True,
    ).start()
    return jsonify({"ok": True})

@app.route("/clear", methods=["POST"])
def clear():
    global _transcript_buffer, _chunk_counter
    with lock:
        state["transcript_chunks"].clear()
        state["notes"].clear()
    _transcript_buffer = []
    _chunk_counter = 0
    broadcast("cleared", {})
    return jsonify({"ok": True})

@app.route("/export", methods=["GET"])
def export_notes():
    fmt = request.args.get("format", "md").lower()
    autoprint = request.args.get("autoprint") == "1"

    if fmt == "html":
        html = _export_html(autoprint=autoprint)
        headers = {} if autoprint else {
            "Content-Disposition": "attachment; filename=lecture_notes.html"
        }
        return Response(html, mimetype="text/html", headers=headers)

    return Response(_export_markdown(), mimetype="text/plain; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=lecture_notes.md"})

def _export_markdown() -> str:
    lines = ["# Lecture Notes\n"]
    for i, note in enumerate(state["notes"], 1):
        lines.append(f"## {i}. {note.get('topic', 'Untitled')}")
        if note.get("summary"):
            lines.append(f"\n_{note['summary']}_\n")
        for b in note.get("bullets", []):
            lines.append(f"- {b}")
        kw = note.get("keywords") or []
        if kw:
            lines.append(f"\n**Keywords:** {', '.join(kw)}")
        lines.append("")
    return "\n".join(lines)

def _export_html(autoprint: bool = False) -> str:
    today = time.strftime("%B %d, %Y")
    cards = []
    for i, n in enumerate(state["notes"], 1):
        topic = _esc(n.get("topic", "Untitled"))
        summary = _esc(n.get("summary", ""))
        bullets = "".join(f"<li>{_esc(b)}</li>" for b in n.get("bullets", []))
        kws = n.get("keywords") or []
        kw_html = ""
        if kws:
            spans = "".join(f"<span class='kw'>{_esc(k)}</span>" for k in kws)
            kw_html = f"<div class='kws'>{spans}</div>"
        lang = (n.get("lang") or "").lower()
        lang_attr = f' data-lang="{lang}"' if lang in ("bn", "en") else ""
        cards.append(f"""
        <article class="card"{lang_attr}>
          <h2><span class="num">{i}.</span> {topic}</h2>
          {f'<p class="summary">{summary}</p>' if summary else ''}
          <ul>{bullets}</ul>
          {kw_html}
        </article>""")

    if not cards:
        cards.append('<p class="empty">No notes recorded yet.</p>')

    auto_script = """
    <script>
      if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(() => setTimeout(() => window.print(), 300));
      } else {
        window.addEventListener('load', () => setTimeout(() => window.print(), 600));
      }
    </script>""" if autoprint else ""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Lecture Notes — {today}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Galada&family=Hind+Siliguri:wght@400;600&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>
  :root {{
    --paper:      #f4ead5;
    --rule:       rgba(139, 108, 62, 0.22);
    --margin-red: rgba(192, 57, 43, 0.4);
    --ink-body:   #2b2416;
    --ink-fade:   #6b5d47;
    --ink-blue:   #2c3e7a;
    --ink-red:    #962d22;
    --highlight:  #fff58a;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    background: var(--paper);
    color: var(--ink-body);
    font-family: 'Crimson Pro', serif;
    line-height: 1.5;
    background-image:
      linear-gradient(to right, transparent 79px, var(--margin-red) 79px,
                      var(--margin-red) 80px, transparent 80px),
      repeating-linear-gradient(transparent 0 31px, var(--rule) 31px 32px);
  }}
  .page {{ max-width: 780px; margin: 0 auto; padding: 50px 60px 50px 100px; }}
  .header {{ border-bottom: 2px solid var(--ink-red); padding-bottom: 12px; margin-bottom: 28px; }}
  .header h1 {{ font-family: 'Caveat', cursive; font-size: 2.6rem; color: var(--ink-blue); margin: 0; line-height: 1; }}
  .header .date {{ font-style: italic; color: var(--ink-fade); font-size: 0.95rem; margin-top: 4px; }}
  .card {{ position: relative; margin: 0 0 36px 0; padding: 18px 24px 16px 24px; background: rgba(255, 252, 240, 0.55); border-radius: 2px; box-shadow: 0 1px 2px rgba(60, 40, 10, 0.06), 0 6px 16px -8px rgba(60, 40, 10, 0.18); page-break-inside: avoid; break-inside: avoid; }}
  .card::before {{ content: ''; position: absolute; top: -9px; left: 26px; width: 64px; height: 20px; background: rgba(255, 200, 200, 0.55); background-image: repeating-linear-gradient(45deg, transparent 0 4px, rgba(255,255,255,0.3) 4px 6px); transform: rotate(-3deg); box-shadow: 0 1px 2px rgba(0,0,0,0.08); }}
  .card:nth-child(3n+2)::before {{ background-color: rgba(180, 220, 200, 0.55); left: auto; right: 36px; transform: rotate(4deg); }}
  .card:nth-child(3n)::before {{ background-color: rgba(255, 235, 180, 0.6); left: 50%; transform: translateX(-50%) rotate(-1.5deg); }}
  .card h2 {{ font-family: 'Caveat', cursive; font-size: 1.85rem; font-weight: 700; color: var(--ink-blue); margin: 0 0 4px 0; line-height: 1.1; }}
  .card[data-lang="bn"] h2 {{ font-family: 'Galada', 'Hind Siliguri', cursive; font-size: 1.55rem; }}
  .num {{ color: var(--ink-red); margin-right: 6px; }}
  .summary {{ font-style: italic; color: var(--ink-fade); font-size: 0.95rem; margin: 6px 0 12px 0; padding-bottom: 8px; border-bottom: 1px dashed rgba(139, 108, 62, 0.35); }}
  .card[data-lang="bn"] .summary {{ font-family: 'Hind Siliguri', sans-serif; font-style: normal; font-size: 1rem; }}
  ul {{ list-style: none; padding: 0; margin: 0; }}
  li {{ font-family: 'Caveat', cursive; font-size: 1.3rem; line-height: 1.45; color: var(--ink-body); padding: 2px 0 2px 24px; position: relative; }}
  .card[data-lang="bn"] li {{ font-family: 'Galada', 'Hind Siliguri', cursive; font-size: 1.15rem; line-height: 1.7; }}
  li::before {{ content: '→'; position: absolute; left: 4px; top: 0; color: var(--ink-red); font-family: 'Caveat', cursive; font-size: 1.4rem; }}
  li:nth-child(2n)::before {{ content: '◦'; font-size: 1.6rem; top: -4px; }}
  li:nth-child(3n)::before {{ content: '✦'; font-size: 1.05rem; top: 2px; }}
  .kws {{ margin-top: 10px; }}
  .kw {{ display: inline-block; font-family: 'Crimson Pro', serif; font-style: italic; font-size: 0.88rem; color: #3a2f00; background: linear-gradient(180deg, transparent 30%, var(--highlight) 30% 90%, transparent 90%); padding: 1px 7px 2px 7px; margin: 0 2px; transform: rotate(-0.5deg); }}
  .kw:nth-child(2n) {{ background: linear-gradient(180deg, transparent 30%, #b8e6c4 30% 90%, transparent 90%); transform: rotate(0.7deg); }}
  .kw:nth-child(3n) {{ background: linear-gradient(180deg, transparent 30%, #ffc6b8 30% 90%, transparent 90%); transform: rotate(-1deg); }}
  .empty {{ color: var(--ink-fade); font-style: italic; text-align: center; padding: 60px 20px; }}
  @page {{ size: A4; margin: 0; }}
  @media print {{
    body {{ background: var(--paper); -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .page {{ padding: 30px 40px 30px 80px; max-width: 100%; }}
    .header h1 {{ font-size: 2.2rem; }}
    .card {{ margin-bottom: 24px; }}
  }}
</style>
</head>
<body>
  <div class="page">
    <div class="header">
      <h1>📓 Lecture Notes</h1>
      <div class="date">{today}</div>
    </div>
    {''.join(cards)}
  </div>
  {auto_script}
</body>
</html>"""


def _esc(s: str) -> str:
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))

if __name__ == "__main__":
    print("🎓 Lecture Note-Taking Agent (Browser Capture · Groq · FREE)")
    print("📌 Open http://localhost:5000 in Chrome / Edge")
    print("🔑 Get free API key: https://console.groq.com")
    app.run(debug=False, threaded=True, port=5000)
