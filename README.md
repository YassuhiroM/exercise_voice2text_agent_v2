# VoiceFlow Clone (Windows 11) — Voice-to-Text Agent

## Environment Setup

Recommended virtual environment name for this machine:
- `venv_ucm_general_python311`

Example setup (Windows PowerShell):

```powershell
python -m venv venv_ucm_general_python311
.\venv_ucm_general_python311\Scripts\Activate.ps1
pip install -r requirements.txt
```

> The code does not hardcode the venv name; the active interpreter is used at runtime.

---

## Style Profile

- **Profile name:** Relaxed but Correct
- **Behavior:** Keep a conversational tone while fixing grammar, punctuation, capitalization, and clarity.
- **Constraint:** Return only rewritten text (no explanations).

System prompt used by Step 4:

> "You are a writing assistant. Rewrite the following text to be relaxed, conversational, but grammatically perfect. Do not add explanations, only return the corrected text."

---

## Project Structure

```text
voiceflow_clone/
  app.py
  config.py
  audio_handler.py
  core/
    __init__.py
    transcriber.py
    style_rewriter.py
```

---

## Step 2 — Audio Capture Implementation

- `audio_handler.py` records microphone audio at 16kHz mono PCM16.
- Audio is streamed directly to a temporary WAV file on disk to avoid large RAM buffers.
- Start/stop/toggle methods are thread-safe.

Expected 10s file size at 16kHz mono PCM16:
- `16000 * 2 * 10 + 44` ≈ `320,044 bytes` (~320 KB)

---

## Step 3 — Bilingual Transcription (ASR)

- `core/transcriber.py` uses `faster-whisper` with:
  - model: `tiny`
  - compute type: `int8`
  - device: `cpu` (or `cuda` when NVIDIA GPU is detected)
- Supports bilingual EN/ES workflow:
  - auto-detect with `language=None`
  - forced language with `language='en'` or `language='es'`
- Cleans temporary audio file after transcription (`delete_audio=True`).

Benchmark notes for Ryzen 5:
- Script prints duration, processing time, and RTF.
- `RTF = processing_time / audio_duration`.

---

## Step 4 — Local LLM Styling (Ollama)

### Plan
- `core/style_rewriter.py` introduces `StyleRewriter` using the local Ollama Python API.
- Before styling starts, the ASR stage should release model memory (e.g., call `Transcriber.unload()` in pipeline orchestration) so CPU/RAM are available for the LLM stage.
- Uses model `llama3.2:1b` and a strict timeout (default 10s) to avoid hanging UI/pipeline flow.

### Edit Code
- Added `StyleRewriter.rewrite(text)` that:
  - validates text,
  - calls `ollama.chat(...)` with the system prompt,
  - returns only the rewritten string.
- Adds robust error handling for:
  - `ConnectionError` when Ollama service is not running,
  - `TimeoutError` for slow responses.

### Run Tools
- Quick test command:
  - `python core/style_rewriter.py --text "hola, i want to go to the park... uhm, maybe tomorrow?"`
- Example expected style output:
  - `Hola, I want to go to the park, maybe tomorrow.`

### Observe
- The script prints request-to-response latency.
- Didactic target on Ryzen 5 7520U for short inputs:
  - often under ~2 seconds after the model is warm.

### Repair
If Ollama is unavailable:
1. Catch `ConnectionError`.
2. Show user guidance: `start Ollama with 'ollama serve'`.
3. Keep pipeline safe: return error state and skip paste action.

---

## Sequential Low-Memory Pipeline

```text
Record -> Stop -> Transcribe (tiny/int8) -> Unload ASR resources -> Rewrite (llama3.2:1b) -> Clipboard/Paste
```
