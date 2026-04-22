# exercise_voice2text_agent_external_model

A local voice-to-text desktop agent for Windows that captures speech with a global hotkey, transcribes audio, rewrites the text with an external language model or Hugging Face model, and pastes the final result into the active window.

## Overview

This project is based on the original `exercise_voice2text_agent_gem` app, but replaces the local rewriting component with a configurable external model provider.

The goal is to preserve the same workflow:

1. Press a hotkey to start recording
2. Capture audio locally
3. Transcribe speech to text
4. Rewrite / correct the transcription with a configurable model
5. Paste the result into the active application

## Main goals

- Keep the same user experience as the original app
- Allow configurable rewriting providers
- Support either:
  - an external LLM API
  - a Hugging Face model
- Maintain a simple, local-first architecture
- Keep setup understandable for non-expert developers

## Features

- Global hotkey-based voice capture
- Local audio recording
- Speech-to-text transcription
- Pluggable text rewriting provider
- Automatic paste into the active window
- Environment-based configuration
- Designed for lightweight Windows usage

## Architecture

The app follows a sequential pipeline:

`Record -> Transcribe -> Rewrite -> Paste`

This keeps the flow simple and reduces resource usage.

### Components

- **Recorder**: captures microphone audio
- **Transcriber**: converts speech to raw text
- **Rewriter**: improves grammar, punctuation, and readability
- **Paster**: inserts final text into the active window
- **Orchestrator**: coordinates the full process

## Project structure

```text
exercise_voice2text_agent_external_model/
├── core/
│   ├── recorder.py
│   ├── transcriber.py
│   ├── rewriter.py
│   ├── paster.py
│   └── orchestrator.py
├── providers/
│   ├── openai_rewriter.py
│   └── huggingface_rewriter.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md





#################
# OLDER VERSION #
#################

# VoiceFlow Clone (Windows 11) — Voice-to-Text Agent v2 (Local + External)

## 🛠 Project Overview
A local, privacy-focused automation agent. It captures voice via a global hotkey, transcribes bilingual speech (EN/ES), styles it via Ollama, and auto-pastes it into the active window.

### Hardware & Environment
* **CPU:** AMD Ryzen 5 7520U
* **RAM:** 8.00 GB (7.28 GB usable) — **Optimized with Sequential Processing.**
* **Python:** 3.11.9 (Stable for AI libraries)

---

## 🏗 System Architecture (Memory Safety)
To prevent system lag, the agent executes tasks sequentially:
1. **Record:** 16kHz Mono audio streamed to disk (~320KB per 10s).
2. **Transcribe:** `faster-whisper` (tiny/int8) processed on CPU.
3. **Style:** Local Hugging-Face's `multilingual mT5‑small model` for grammar correction, cost‑free usage; External option the low‑cost model `GPT‑4.1 Nano`
4. **Paste:** `pyautogui` injection into active cursor.

---

## 📁 Project Structure
```text
exercise_voice2text_agent_gem/
├── core/
│   ├── transcriber.py      # DONE: Whisper-tiny integration
│   ├── style_rewriter.py   # DONE: 
│   └── clipboard_paster.py # DONE: Automation logic
├── audio_handler.py        # DONE: PyAudio recording logic
├── main.py                 # DONE: Orchestrator & Hotkey Listener
├── requirements.txt        # DONE: Verified dependencies
└── README.md               # DONE: Final Documentation