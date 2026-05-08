# PrepMate AI — IELTS & GRE Coaching Chatbot

> A browser-based AI study partner for IELTS and GRE preparation, powered by the Groq API and built on top of a voice-enabled English practice bot.

---

## What It Does

PrepMate AI acts as a personalised exam coach. You pick your exam and section, then have a back-and-forth conversation — typing or speaking — where the AI gives you practice questions, evaluates your answers, scores your writing and speaking, and explains every mistake in detail.

It knows the real structure of each exam and adapts its behaviour accordingly. An IELTS Writing session behaves like a writing examiner. A GRE Quant session behaves like a maths tutor. They are not the same bot with a different label.

---

## Exams Covered

### IELTS — 4 Sections

| Section | What the AI Does |
|---|---|
| 🎧 **Listening** | Simulates all 4 section types via text transcripts. Teaches distractor avoidance and signpost language. Covers form fill, MCQ, matching, and map labelling. |
| 📖 **Reading** | Full passages with all question types — T/F/Not Given, Matching Headings, MCQ, Summary Completion. Explains the exact difference between *False* and *Not Given* (the most common student mistake). |
| ✍️ **Writing** | Task 1 Academic (graphs, maps, processes), Task 1 General Training (formal/semi-formal/informal letters), Task 2 (all 5 essay types). Scores on all 4 official band descriptors with line-by-line feedback. |
| 🗣️ **Speaking** | Parts 1, 2, and 3 with correct timing guidance. Scores on fluency, vocabulary, grammar, and pronunciation. Teaches PEEL structure for Part 3 extended answers. |

### GRE — 3 Sections

| Section | What the AI Does |
|---|---|
| 🔤 **Verbal Reasoning** | Text Completion (1/2/3-blank), Sentence Equivalence (both answers must create similar meaning — not just be synonyms), Reading Comprehension (main idea, inference, tone, strengthen/weaken). Teaches high-frequency vocabulary with etymology. |
| 📐 **Quantitative Reasoning** | All 4 question types: Quantitative Comparison, single-answer MCQ, all-that-apply MCQ, and numeric entry. Covers arithmetic, algebra, geometry, and data analysis with step-by-step solutions and trap explanations. |
| ⚖️ **Analytical Writing** | Issue Essay (give and defend your position) vs Argument Essay (critique someone else's reasoning — never state your own opinion). Scores 0–6 with rubric-based feedback and suggested rewrites. |

---

## Features

- **Voice input** — Uses the browser's Web Speech API. Click the mic, speak naturally, the text is sent automatically.
- **Text-to-speech** — In the Speaking section, the AI reads its responses aloud to simulate a real examiner interaction.
- **Section-aware system prompts** — Each section has a dedicated, detailed system prompt. The AI knows band descriptors, question type rules, common traps, and scoring criteria for its specific section.
- **Subtabs** — Each section has 4–6 subtabs (e.g., "Quantitative Comparison", "Problem Solving", "Data Analysis") that narrow the AI's focus.
- **Sidebar shortcuts** — Click any topic in the sidebar (e.g., "True / False / Not Given", "Hasty Generalization") to jump straight into that practice type.
- **Quick starter prompts** — Each section's welcome screen has 4 one-click prompts to start a session immediately.
- **Band / score chips** — Band scores and numerical scores are highlighted inline in the chat.
- **Conversation memory** — The full conversation history is sent with every request so the AI maintains context across multiple turns.
- **Free to use** — Runs on the Groq free tier. No credit card required. The API key stays in your browser and is never stored.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML, CSS, JavaScript — single file, no build step |
| AI Model | `llama-3.3-70b-versatile` via Groq API |
| API Format | OpenAI-compatible (`/openai/v1/chat/completions`) |
| Voice Input | Web Speech API — `SpeechRecognition` |
| Voice Output | Web Speech API — `SpeechSynthesis` |
| Styling | Custom CSS with CSS variables — no frameworks |
| Fonts | Playfair Display (headings) + DM Sans (body) via Google Fonts |

---

## Setup

1. Get a free Groq API key at [console.groq.com/keys](https://console.groq.com/keys) — takes about 60 seconds, no credit card needed.
2. Open `PrepMate-AI.html` in **Chrome or Edge** (required for voice input via Web Speech API; other browsers support text-only mode).
3. Paste your API key in the setup screen.
4. Select your exam (IELTS or GRE) and a section.
5. Start practising.

> **Note:** The mic button requires microphone permission from your browser. If you prefer text-only, just type in the input box and press Enter or the send button.

---

## Groq Free Tier Limits

The free tier is sufficient for personal study use.

| Limit | Value |
|---|---|
| Requests per minute | 30 |
| Tokens per minute | 6,000 |
| Requests per day | 14,400 |
| Cost if exceeded | Nothing — returns a 429 error, never charges |

A typical exchange uses 400–800 tokens. You would need to send messages continuously for hours to approach the daily limit alone.

---

## How It Compares to the Original Project

This project is a restructured version of a Gemini-powered English Practice Bot.

| Feature | Original | PrepMate AI |
|---|---|---|
| AI backend | Google Gemini API | Groq API (llama-3.3-70b) |
| Purpose | General English conversation | IELTS & GRE exam preparation |
| Exam structure | Not exam-aware | Full IELTS 4-section + GRE 3-section structure |
| Scoring | None | Band 0–9 (IELTS), Score 0–6 (GRE AWA), criterion-level feedback |
| Question types | General chat | All official exam question types per section |
| Voice | Speaking practice only | All sections (mic input + TTS for Speaking) |
| Navigation | Single mode | Subtabs + sidebar per section |
| Setup screen | Hardcoded API key | API key input + exam + section selector |

---

## Project Structure

```
PrepMate-AI.html      ← entire application (HTML + CSS + JS, single file)
README.md             ← this file
Study.txt             ← reference notes on AI API providers
```

---

## Is This Enough for Full Exam Preparation?

**No — not on its own.** PrepMate AI is a genuinely useful daily practice tool, but it has real limitations you should understand before relying on it.

### What It Does Well

- Unlimited practice questions on demand, any time
- Instant feedback on writing with band scores
- Vocabulary drilling, especially for GRE Verbal
- Speaking practice when you have no conversation partner
- Explaining concepts and strategies (T/F/NG distinction, QC traps, AWA structure, etc.)
- Zero cost — which means you can use it daily without worrying

### Where It Falls Short

**🎧 IELTS Listening** is the biggest gap. The real exam uses audio recordings with accents (British, Australian, American), background noise, and natural speech pace. No text transcript can replicate that. You *must* use official Cambridge IELTS audio for this section.

**📐 GRE Quant** — the AI can make arithmetic mistakes. LLMs are not calculators. Always verify solutions yourself, especially for complex algebra or geometry. Use it to understand *strategies*, not to confirm answers.

**✍️ Writing scoring is approximate.** The AI can give useful feedback but it is not a certified IELTS examiner. Band scores could be off by 0.5–1.0 band in either direction. For serious prep, submit at least 2–3 essays to a real teacher or verified scoring service.

**⏱ No real exam simulation.** Actual exams have strict timing, pressure, and a specific interface. PrepMate does not simulate that environment.

### Recommended Study Plan

Use PrepMate as your daily practice partner alongside official materials:

| Resource | Purpose |
|---|---|
| **PrepMate AI** | Daily practice, concept explanations, vocabulary, unlimited questions |
| **Cambridge IELTS books 1–18** | Official past papers — the gold standard for all 4 sections |
| **ielts.org / ets.org** | Official sample tests, scoring guides, and exam information |
| **Official audio (Cambridge / BBC)** | Real Listening practice with accents and natural pace |
| **1–2 real teacher evaluations** | Calibrate your actual writing band score |
| **Timed mock tests** | Build exam stamina and time management under pressure |

> **Bottom line:** Use PrepMate for daily practice — it is genuinely better than studying alone from a textbook. Treat it as a supplement, not a replacement for official materials and occasional real feedback.

---

## Technical Limitations

- **No audio playback for Listening** — the Web Speech API does not generate natural listening audio, so Listening practice is text-transcript based. This is a limitation of browser-only apps.
- **Voice input requires Chrome/Edge** — Firefox and Safari have limited or no support for `SpeechRecognition`.
- **No persistent storage** — conversation history resets on page refresh. This is intentional for privacy.
- **Single user** — designed for one person's personal study, not multi-user deployment.

