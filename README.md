Voice2Text Agent (Spanish)

This project is a desktop voice‑to‑text agent designed for Windows that captures Spanish speech, transcribes it locally using faster‑whisper
, optionally rewrites the transcript with a configurable grammar‑correction model, and pastes the result into the active application. It evolved from the exercise_voice2text_agent_gem project and now supports external rewriters via Hugging Face mT5 or OpenAI models. This version of the agent is maintained in the exercise_voice2text_agent_v2 repository.

Features
Push‑to‑talk recording: Press and hold Ctrl + Alt + Space to start recording and release to stop. The recorder also auto‑stops after a configurable period of silence.
Local transcription: Uses faster‑whisper to transcribe audio on CPU. Spanish (es) transcription is the default and can be changed via configuration.
Configurable rewriting: After transcription, text can be rewritten or grammar‑corrected by either a Hugging Face mT5 model or an OpenAI Chat model, depending on your .env settings. Short transcripts (fewer than three words) skip rewriting, and the system automatically falls back to the raw transcript if the rewrite looks corrupted.
Clipboard and paste automation: The final text is copied to the clipboard and pasted into the focused window using a simulated Ctrl+V.
Low memory usage: The pipeline is fully sequential, so peak RAM stays low and is suitable for 8 GB systems.
Silence detection: Recording stops automatically after ~5 seconds of silence using a simple energy threshold.
Requirements
Windows 10 or later
Python 3.11 (or compatible)
CPU with AVX instructions (for faster‑whisper models)
Microphone input
At least 8 GB of RAM

See requirements.txt for Python dependencies. The project uses PyAudio for audio capture, faster‑whisper for ASR, transformers/openai for rewriting, and pyautogui/pyperclip for clipboard automation.

Installation

Clone the repository:

git clone https://github.com/YassuhiroM/exercise_voice2text_agent_v2.git
cd exercise_voice2text_agent_v2

Create and activate a virtual environment:

python -m venv .venv
.venv\Scripts\activate  # Windows

Install dependencies:

pip install -r requirements.txt
Configuration

Copy .env.example to .env and set your desired options:

REWRITER_PROVIDER=huggingface     # or "openai"
OPENAI_API_KEY=sk-...             # only needed when using OpenAI
HF_MODEL_NAME=dreuxx26/Multilingual-grammar-Corrector-using-mT5-small
OPENAI_MODEL=gpt-4.1-nano         # for OpenAI mode
REWRITER_PROVIDER: Choose huggingface to use a local mT5 model or openai to call OpenAI’s Chat API.
HF_MODEL_NAME and OPENAI_MODEL specify the Hugging Face and OpenAI models respectively.
To change transcription settings (model size, language, device), edit the instantiation of Transcriber in core/transcriber.py.
Usage

From an activated virtual environment, run:

python main.py

Then:

Hold Ctrl + Alt + Space to begin recording.
Speak clearly into your microphone.
Release any of the keys to stop recording; the transcription and rewriting stages will run sequentially.
The recorder will also auto‑stop after 5 seconds of silence.
The corrected transcript will be pasted into the focused application.
Press ESC in the terminal to exit.
Project Structure

The key modules are organized as follows:

exercise_voice2text_agent_v2/
├── core/
│   ├── audio_handler.py      # Handles audio recording with silence detection:contentReference[oaicite:11]{index=11}.
│   ├── transcriber.py        # Wraps faster‑whisper for transcription:contentReference[oaicite:12]{index=12}.
│   ├── external_rewriter.py  # Grammar correction via Hugging Face or OpenAI:contentReference[oaicite:13]{index=13}.
│   ├── orchestrator.py       # Coordinates recording, transcription, rewriting, and pasting:contentReference[oaicite:14]{index=14}.
│   └── clipboard_paster.py   # Copies text to clipboard and sends Ctrl+V:contentReference[oaicite:15]{index=15}.
├── main.py                   # Entry point, sets up global hotkeys.
├── requirements.txt          # Python dependencies.
├── .env.example              # Example environment variables.
└── README.md                 # Project documentation.
Customization
Transcription model: Change the model_size (e.g., small, medium) or language in core/transcriber.py.
Silence timeout and threshold: Adjust TIMEOUT_LIMIT and SILENCE_THRESHOLD in core/audio_handler.py to tune auto‑stop behavior.
Heuristics: Modify _min_words_for_rewrite or _min_overlap_ratio in core/orchestrator.py to control when rewriting occurs.
License

MIT License

Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
