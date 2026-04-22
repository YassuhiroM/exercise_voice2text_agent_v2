# exercise_voice2text_agent_v2

A local voice-to-text desktop agent for Windows that captures speech with a global hotkey, transcribes audio with `faster-whisper`, rewrites the text with a configurable external model (Hugging Face or OpenAI), and pastes the final result into the active window.

---

## Overview

This project evolved from `exercise_voice2text_agent_gem` (which used a local Ollama model for rewriting) and replaces that component with a configurable external provider.

The workflow is the same:

1. Hold **Ctrl+Alt+Space** to start recording
2. Release to stop (or auto-stop after 5 s of silence)
3. Transcribe speech to text locally via `faster-whisper`
4. Rewrite / grammar-correct with a configurable model
5. Paste the result into the active application via `Ctrl+V`

---

## Hardware & Environment

- **CPU:** AMD Ryzen 5 7520U
- **RAM:** 8 GB — sequential processing keeps peak RAM low
- **Python:** 3.11

---

## Architecture

```
Record → Transcribe → Rewrite → Paste
```

Processing is fully sequential to minimise memory usage on low-RAM machines.

### Components

| Module | Role |
|---|---|
| `main.py` | Entry point; global hotkey listener (Ctrl+Alt+Space / ESC) |
| `core/orchestrator.py` | Coordinates the full pipeline; handles push-to-talk + auto-stop |
| `core/audio_handler.py` | PyAudio recorder with silence-detection auto-stop |
| `core/transcriber.py` | `faster-whisper` ASR (CPU, int8, Spanish by default) |
| `core/external_rewriter.py` | Grammar correction via Hugging Face mT5 or OpenAI |
| `core/clipboard_paster.py` | Copies text to clipboard and sends Ctrl+V |

---

## Project Structure

```text
exercise_voice2text_agent_v2/
├── core/
│   ├── __init__.py
│   ├── audio_handler.py
│   ├── clipboard_paster.py
│   ├── external_rewriter.py
│   ├── orchestrator.py
│   └── transcriber.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```env
REWRITER_PROVIDER=huggingface     # or "openai"
OPENAI_API_KEY=your-openai-key    # only needed when using openai
HF_MODEL_NAME=dreuxx26/Multilingual-grammar-Corrector-using-mT5-small
OPENAI_MODEL=gpt-4.1-nano         # or gpt-4o-mini
```

---

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Run

```bash
python main.py
```

- Hold **Ctrl+Alt+Space** → recording starts
- Release any of those keys → recording stops, pipeline runs, text is pasted
- Recording also auto-stops after **5 seconds of silence**
- Press **ESC** to exit
