# VoiceFlow Clone (Windows 11) — Voice-to-Text Agent

## 🛠 Project Overview
A local, privacy-focused automation agent for Windows 11. It captures voice via a global hotkey, transcribes bilingual speech (EN/ES), styles the text for a "relaxed but correct" tone, and auto-pastes it into the active window.

### Hardware Context
* **CPU:** AMD Ryzen 5 7520U (2.80 GHz)
* **RAM:** 8.00 GB (7.28 GB usable) — **Optimized for Sequential Pipeline.**
* **OS:** Windows 11

---

## 🏗 System Architecture (8GB RAM Strategy)
To prevent system freezing, this agent uses a **Sequential Pipeline**:
1. **Record:** Stream audio to disk (RAM footprint < 50MB).
2. **Transcribe:** Load `faster-whisper` (tiny/int8), process, then release resources.
3. **Style:** Call local `Ollama` API (`llama3.2:1b`).
4. **Paste:** Use `pyautogui` for clipboard injection (`CTRL+V`).

---

## 🚀 Setup & Usage

### 1. Environment (Python 3.11 Required)
```powershell
python -m venv venv_ucm_general_python311
.\venv_ucm_general_python311\Scripts\Activate.ps1
pip install -r requirements.txt
2. Local Models
ASR: Handled automatically by faster-whisper.

Styling: Install Ollama and run:
ollama pull llama3.2:1b

📁 Project Structure
Plaintext
exercise_voice2text_agent_gem/
├── core/
│   ├── transcriber.py      # DONE: Whisper-tiny integration
│   ├── style_rewriter.py   # DONE: Ollama 1B styling
│   └── clipboard_paster.py # DONE: Automation logic
├── audio_handler.py        # DONE: PyAudio recording logic
├── main.py                 # DONE: Orchestrator & Hotkey Listener
├── requirements.txt        # DONE: Dependency list
└── README.md               # DONE: Documentation
