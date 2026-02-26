# VoiceFlow Clone (Windows 11) — Voice-to-Text Agent

## 🛠 Project Overview
A local, privacy-focused automation agent for Windows 11. It captures voice via a global hotkey, transcribes bilingual speech (EN/ES), styles text to a "relaxed but correct" tone via Ollama, and auto-pastes it into any active window.

### Hardware Context (Target System)
* **CPU:** AMD Ryzen 5 7520U (2.80 GHz)
* **RAM:** 8.00 GB (7.28 GB usable) — Optimized for low-memory footprint.
* **OS:** Windows 11

---

## 🏗 System Architecture (Sequential Pipeline)
To protect the 8GB RAM limit, the app runs in stages:
1. **Record:** Direct-to-disk 16kHz WAV streaming.
2. **Transcribe:** `faster-whisper` (tiny/int8) converts audio to raw text.
3. **Style:** Local `Ollama` (llama3.2:1b) polishes the grammar.
4. **Paste:** `pyautogui` injects the result via `CTRL+V`.

---

## 📁 Repository Structure
```text
exercise_voice2text_agent_gem/
├── core/
│   ├── transcriber.py      # Faster-Whisper wrapper
│   ├── style_rewriter.py   # Ollama API integration
│   └── clipboard_paster.py # PyAutoGUI automation
├── audio_handler.py        # Thread-safe PyAudio recording
├── main.py                 # App entrypoint & Hotkey listener (CTRL+ALT+SPACE)
├── requirements.txt        # Optimized dependencies
└── README.md               # Documentation
