# exercise_voice2text_agent_v2

A desktop voice-to-text agent for Windows that captures Spanish speech, transcribes audio locally with `faster-whisper`, optionally rewrites the transcript with a configurable grammar-correction model, and pastes the final text into the active application.

---

## Overview

This project evolved from `exercise_voice2text_agent_gem` and now supports external rewriters via Hugging Face mT5 or OpenAI models.

The workflow is:

1. Hold **Ctrl+Alt+Space** to start recording
2. Release to stop (or let auto-stop trigger after silence)
3. Transcribe speech locally via `faster-whisper`
4. Rewrite or grammar-correct text via Hugging Face or OpenAI
5. Paste the final result into the focused app with `Ctrl+V`

---

## Features

- **Push-to-talk recording:** Press and hold **Ctrl+Alt+Space** to start; release to stop.
- **Local transcription:** Uses `faster-whisper` on CPU. Spanish (`es`) is the default language.
- **Configurable rewriting:** Uses either Hugging Face mT5 or OpenAI Chat based on `.env` settings.
- **Rewrite safeguards:** Short transcripts (fewer than three words) skip rewriting, and the system falls back to raw text when rewrite output appears corrupted.
- **Clipboard and paste automation:** Copies final text to the clipboard and pastes into the active window.
- **Low memory usage:** Fully sequential pipeline keeps RAM usage suitable for 8 GB systems.
- **Silence detection:** Automatically stops after around 5 seconds of silence using an energy threshold.

---

## Requirements

- Windows 10 or later
- Python 3.11 (or compatible)
- CPU with AVX instructions (for `faster-whisper` models)
- Microphone input
- At least 8 GB RAM

See `requirements.txt` for Python dependencies. The project uses PyAudio for audio capture, `faster-whisper` for ASR, `transformers`/`openai` for rewriting, and `pyautogui`/`pyperclip` for clipboard automation.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YassuhiroM/exercise_voice2text_agent_v2.git
cd exercise_voice2text_agent_v2
```

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Copy `.env.example` to `.env` and set your options:

```env
REWRITER_PROVIDER=huggingface     # or "openai"
OPENAI_API_KEY=sk-...             # only needed when using OpenAI
HF_MODEL_NAME=dreuxx26/Multilingual-grammar-Corrector-using-mT5-small
OPENAI_MODEL=gpt-4.1-nano         # for OpenAI mode
```

- `REWRITER_PROVIDER`: Choose `huggingface` to use local mT5 or `openai` to call OpenAI Chat API.
- `HF_MODEL_NAME` and `OPENAI_MODEL`: Select the Hugging Face and OpenAI models.
- To change transcription settings (model size, language, device), edit `Transcriber` in `core/transcriber.py`.

---

## Usage

From an activated virtual environment, run:

```bash
python main.py
```

Then:

- Hold **Ctrl+Alt+Space** to begin recording.
- Speak clearly into your microphone.
- Release any of those keys to stop recording; transcription and rewriting run sequentially.
- Recording also auto-stops after about 5 seconds of silence.
- The corrected transcript is pasted into the focused application.
- Press **ESC** in the terminal to exit.

---

## Project Structure

The key modules are organized as follows:

```text
exercise_voice2text_agent_v2/
├── core/
│   ├── audio_handler.py      # Handles audio recording with silence detection.
│   ├── transcriber.py        # Wraps faster-whisper transcription.
│   ├── external_rewriter.py  # Grammar correction via Hugging Face or OpenAI.
│   ├── orchestrator.py       # Coordinates recording, transcription, rewriting, and pasting.
│   └── clipboard_paster.py   # Copies text to clipboard and sends Ctrl+V.
├── main.py                   # Entry point and global hotkey setup.
├── requirements.txt          # Python dependencies.
├── .env.example              # Example environment variables.
└── README.md                 # Project documentation.
```

---

## Customization

- **Transcription model:** Change `model_size` (for example `small`, `medium`) or language in `core/transcriber.py`.
- **Silence timeout and threshold:** Adjust `TIMEOUT_LIMIT` and `SILENCE_THRESHOLD` in `core/audio_handler.py`.
- **Rewrite heuristics:** Modify `_min_words_for_rewrite` or `_min_overlap_ratio` in `core/orchestrator.py`.

---

## License

MIT License

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you want to change.
