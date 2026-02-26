# VoiceFlow Clone (Windows 11) — Voice-to-Text Agent

## Step 1 — Plan

This repository starts with the **planning phase** for a low-memory voice-to-text desktop agent for Windows 11.

### Objectives
- Record microphone audio with a global hotkey (`CTRL+ALT+SPACE`).
- Transcribe bilingual speech (English/Spanish) using `faster-whisper` (`tiny`).
- Rewrite text with Ollama (`llama3.2:1b`) in a relaxed but grammatically correct style.
- Copy rewritten text to clipboard and auto-paste with `CTRL+V`.
- Show live state in a lightweight CustomTkinter overlay.

---

## Proposed Project Structure

```text
voiceflow_clone/
  app.py                     # App entrypoint; starts GUI + service coordination
  config.py                  # Config values (hotkeys, model names, temp paths)
  gui/
    overlay.py               # CustomTkinter small status window
  core/
    orchestrator.py          # Sequential pipeline coordinator and state machine
    hotkey_listener.py       # Non-blocking pynput listener and key-state tracking
    audio_handler.py         # PyAudio recorder to temp WAV files (thread-safe)
    transcriber.py           # faster-whisper wrapper (load, transcribe, unload)
    style_rewriter.py        # Ollama client wrapper (rewrite prompt + timeout)
    clipboard_paster.py      # Clipboard write + Ctrl+V automation
  tests/
    test_hotkey_listener.py  # Hotkey toggle behavior with mocked key events
    test_pipeline_flow.py    # Sequential state transitions and lock behavior
    test_clipboard.py        # Clipboard + paste invocation mocks
```

---

## Step 2 — Audio Capture Implementation (Development Loop)

### Plan
- Use a `Recorder` class in `audio_handler.py` based on **PyAudio**.
- Keep memory usage low by writing incoming microphone chunks directly into a temporary `.wav` file on disk.
- Use a fixed **16kHz**, **mono**, **16-bit PCM** stream (Whisper-friendly, smaller files).
- Make start/stop thread-safe with a lock so a hotkey toggle cannot race under rapid key presses.

### Edit Code
- Added `audio_handler.py` with:
  - `Recorder.start()` to initialize PyAudio input and temp WAV output.
  - `Recorder.stop()` to close stream/file/driver safely.
  - `Recorder.toggle()` for start/stop behavior from `main.py`.
  - `DeviceNotFoundError` for disconnected/unavailable microphone handling.

### Run Tools
- Standalone test is included in:
  - `python audio_handler.py`
- It records for 3 seconds and prints output path + file size.

### Observe
- Expected data size for 10 seconds at 16kHz mono PCM16:
  - `16000 samples/sec * 2 bytes/sample * 10 sec = 320,000 bytes`
  - Plus WAV header (~44 bytes) => approximately **320 KB**.
- This footprint is compact and does not grow RAM significantly because data is streamed to disk.

### Repair
If microphone is disconnected / unavailable ("Device Not Found"):
1. Catch and raise `DeviceNotFoundError` with user-readable guidance.
2. In GUI/main flow, set status to: `Microphone unavailable — reconnect and retry`.
3. Suggest user checks Windows input device settings and closes conflicting apps.
4. Keep pipeline idle; do not proceed to transcription until a valid file exists.

### Update Docs
- This section documents how audio buffering is handled and why it is memory-safe on 8GB RAM.

---

## Non-Blocking Hotkey Design (`pynput`)

### Why this design
`pynput.keyboard.Listener` is event-driven and can run in its own thread. We use that thread only to detect key combinations and dispatch a small callback to avoid blocking input handling.

### Key principles
1. **Listener thread only detects events** (very small operations).
2. **Main pipeline work runs elsewhere** (worker thread / queue) to keep UI responsive.
3. **Debounce toggle** so one key press cannot trigger multiple start/stop transitions.
4. **State lock** ensures start/stop cannot race.

### Event flow
1. Track pressed keys in a `set` (`ctrl`, `alt`, `space`).
2. On each `on_press`, check if all three are present.
3. If combination becomes active and debounce gate is open:
   - push `TOGGLE_RECORDING` event to a thread-safe queue.
   - close debounce gate.
4. On `on_release`, remove key from set.
5. When any required key is released, reopen debounce gate.

### Thread model
- **Thread A (GUI/Main):** CustomTkinter loop and status rendering.
- **Thread B (Hotkey listener):** pynput keyboard listener.
- **Thread C (Pipeline worker):** Handles sequential stages:
  1. Recording
  2. Transcription
  3. Styling
  4. Clipboard + paste

Only Thread C performs heavy operations. This prevents RAM spikes and keeps CPU usage more predictable on 8GB systems.

---

## Memory-Safe Sequential Pipeline (8GB Strategy)

- Keep only one heavy model actively used at a time.
- After transcription completes, release transcriber references and run GC.
- Run styling step only after audio/transcription objects are released.
- Keep audio files short and temporary (`.wav` in temp folder), then delete.
- Use bounded queues and small buffers to avoid accumulating frames.

Target flow:

```text
Record -> Stop -> Transcribe (tiny) -> Release resources -> Rewrite (Ollama 1B) -> Clipboard/Paste
```
