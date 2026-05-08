# PrepMate AI — Project Description

**PrepMate AI** is a browser-based IELTS and GRE preparation chatbot built as a single HTML file. It uses the Groq API (free tier) to power an AI coach that knows the real structure of each exam — not just general English assistance.

---

## The Problem It Solves

Generic AI chatbots can help with English, but they don't know the difference between IELTS Task 1 Academic and Task 1 General Training. They don't know that the GRE Argument Essay requires you to *never* state your own opinion. They can't score a speaking response against the 4 official IELTS band descriptors, or explain why a Quantitative Comparison answer is "Cannot be Determined."

PrepMate AI is built around the actual rules of each exam section.

---

## Exam Coverage

**IELTS** — all 4 official sections:
- **Listening** (Sections 1–4, all question types, distractor training)
- **Reading** (T/F/Not Given, Matching Headings, Summary Completion — with the exact distinctions that trip students up)
- **Writing** (Task 1 Academic graphs/maps/processes, Task 1 General letters with correct register, Task 2 all 5 essay types — scored on all 4 band descriptors)
- **Speaking** (Parts 1/2/3 with correct timing, PEEL structure for Part 3, band scoring on fluency/vocabulary/grammar/pronunciation)

**GRE** — all 3 official sections:
- **Verbal Reasoning** (Text Completion with 1/2/3 blanks, Sentence Equivalence with "similar meaning" rule, Reading Comprehension, high-frequency vocabulary with etymology)
- **Quantitative Reasoning** (Quantitative Comparison traps, all-that-apply MCQ, numeric entry, arithmetic/algebra/geometry/data analysis with step-by-step solutions)
- **Analytical Writing** (Issue Essay vs Argument Essay — the distinction most students miss — scored 0–6 with rubric-based feedback)

---

## How It Works

1. User enters a free Groq API key and selects their exam + section
2. Each section loads a detailed, exam-specific system prompt — the AI knows scoring criteria, question type rules, and common traps for that specific section
3. User practises by typing or speaking (Web Speech API)
4. In the Speaking section, the AI also speaks its responses aloud
5. The full conversation history is maintained so the AI remembers context across turns

---

## Built With

- Single-file HTML + CSS + Vanilla JavaScript (no build step, no framework)
- Groq API — `llama-3.3-70b-versatile` model via OpenAI-compatible endpoint
- Web Speech API — microphone input and text-to-speech output
- Playfair Display + DM Sans — dark navy/gold theme

---

## Origin

Restructured and extended from a Gemini-powered English Practice Bot. The original used the Google Gemini API for general conversation. This version replaces the backend with Groq, replaces the single-mode interface with a proper exam-section structure, and replaces the generic system prompt with section-specific coaching prompts built around real exam criteria.
