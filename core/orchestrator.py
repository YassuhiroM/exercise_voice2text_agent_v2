from __future__ import annotations

"""VoiceFlow end-to-end orchestrator.

Goals:
- Link recording -> transcription -> styling -> clipboard paste.
- Keep memory usage low on 8GB systems via sequential processing + gc.collect().
- Print clear status updates for each pipeline stage.
- Avoid double-processing (manual stop + watcher thread).
- Support push-to-talk + optional recorder auto-stop behavior safely.

Diagnostics (added):
- Print audio metadata (sr/ch/duration)
- Print RAW transcript vs FINAL rewritten text
- Heuristics: skip rewrite for very short text; fallback to RAW if rewrite looks corrupted
"""

import gc
import threading
import time
import wave
from pathlib import Path

from core.audio_handler import Recorder
from core.clipboard_paster import Paster
from core.external_rewriter import ExternalRewriter
from core.transcriber import Transcriber


def _audio_meta(path: Path) -> str:
    """Best-effort WAV metadata to catch sampling issues."""
    try:
        with wave.open(str(path), "rb") as wf:
            ch = wf.getnchannels()
            sr = wf.getframerate()
            nframes = wf.getnframes()
            dur = nframes / float(sr) if sr else 0.0
            sw = wf.getsampwidth()
        return f"{ch}ch {sr}Hz {dur:.2f}s sampwidth={sw}"
    except Exception:
        return "unknown"


def _token_overlap_ratio(a: str, b: str) -> float:
    """Cheap similarity check to detect 'rewriter hallucinated nonsense'."""
    ta = {t for t in a.lower().split() if t}
    tb = {t for t in b.lower().split() if t}
    if not ta:
        return 0.0
    return len(ta & tb) / len(ta)


class VoiceFlowOrchestrator:
    """Coordinates the full voice-to-text pipeline from hotkey events."""

    def __init__(self) -> None:
        self.recorder = Recorder()
        self.transcriber = Transcriber(keep_model_loaded=False)
        self.rewriter = ExternalRewriter(timeout_seconds=10.0)
        self.paster = Paster(paste_delay_seconds=0.1)

        # ---- state / concurrency guards ----
        self.is_processing: bool = False
        self._lock = threading.Lock()

        self._current_audio_path: Path | None = None
        self._last_processed_path: Path | None = None

        # After an auto-stop completes, key-release may still call toggle().
        # Ignore "start" toggles for a short window to avoid accidental new recordings.
        self._ignore_start_until: float = 0.0  # monotonic seconds

        # ---- heuristics ----
        self._min_words_for_rewrite = 3          # skip rewrite only for very short clips
        self._min_overlap_ratio = 0.15           # ASR rewrites can change many words legitimately

    # ---------------------------------------------------------------------
    # Public API (keeps compatibility with your existing main.py)
    # ---------------------------------------------------------------------
    def toggle(self) -> None:
        """Toggle recording state. Used by hotkey press/release."""
        if not self.recorder.is_recording and time.monotonic() < self._ignore_start_until:
            return

        if not self.recorder.is_recording:
            self.start_recording()
        else:
            self.stop_and_process()

    def start_recording(self) -> None:
        """Starts recording and spawns a watcher thread that processes if recorder stops itself."""
        with self._lock:
            if self.recorder.is_recording:
                return
            if self.is_processing:
                print("[INFO] Busy processing previous audio. Please wait.")
                return

            audio_path = self.recorder.start()
            self._current_audio_path = audio_path
            print(f"[RECORDING] Listening... saving to {audio_path}")

            threading.Thread(
                target=self._wait_for_auto_stop,
                args=(audio_path,),
                daemon=True,
            ).start()

    def stop_and_process(self) -> None:
        """Stops recording (manual stop) and processes the resulting audio once."""
        audio_path = self.recorder.stop()
        if not audio_path:
            print("[ERROR] Recorder returned no audio path.")
            return

        print("[RECORDING] Stopped.")
        self._process_recording_once(audio_path, source="manual-stop")

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _wait_for_auto_stop(self, audio_path: Path) -> None:
        """Watches recorder and processes if it stops without a manual stop call."""
        while self.recorder.is_recording:
            time.sleep(0.1)

        self._process_recording_once(audio_path, source="auto-stop")
        self._ignore_start_until = time.monotonic() + 0.75

    def _process_recording_once(self, audio_path: Path | None, source: str) -> None:
        """Ensures a given audio path is processed at most once."""
        if audio_path is None:
            return

        with self._lock:
            if self._last_processed_path == audio_path:
                return
            if self.is_processing:
                return

            self.is_processing = True
            self._last_processed_path = audio_path

        try:
            self._process_recording(audio_path, source=source)
        finally:
            with self._lock:
                self.is_processing = False
                self._current_audio_path = None

    def _process_recording(self, audio_path: Path, source: str) -> None:
        """Runs the full pipeline: transcribe -> style -> paste -> cleanup."""
        if not audio_path.exists():
            print("[ERROR] Empty audio path or file missing. Please record again.")
            return

        raw_text = ""
        final_text = ""
        try:
            print(f"[AUDIO] {source}: {_audio_meta(audio_path)}")

            print("[TRANSCRIBING] Processing recorded audio...")
            raw_text = self.transcriber.transcribe(audio_path=audio_path, delete_audio=False).strip()

            print(f"[RAW] {raw_text}")

            if not raw_text:
                print("[ERROR] Empty audio detected (stopped too quickly or silence only).")
                return

            gc.collect()

            # Heuristic: very short transcripts are safer without rewriting
            raw_words = raw_text.split()
            if len(raw_words) < self._min_words_for_rewrite:
                print("[STYLING] Skipping rewrite (text too short).")
                final_text = raw_text
            else:
                print("[STYLING] Refining text...")
                try:
                    final_text = (self.rewriter.rewrite(raw_text) or "").strip()
                except (ConnectionError, TimeoutError) as exc:
                    print(f"[STYLING] Fallback to raw transcript: {exc}")
                    final_text = raw_text

                # If rewriter output looks corrupted, fallback to raw
                overlap = _token_overlap_ratio(raw_text, final_text)
                if not final_text or overlap < self._min_overlap_ratio:
                    print(f"[STYLING] Rewrite looks corrupted (overlap={overlap:.2f}). Falling back to RAW.")
                    final_text = raw_text

            print(f"[FINAL] {final_text}")

            print("[PASTING] Copying to clipboard and sending Ctrl+V...")
            self.paster.paste_text(final_text)
            print("[PASTING] Done.")
        except FileNotFoundError as exc:
            print(f"[ERROR] Recorder output file not found: {exc}")
        except RuntimeError as exc:
            print(f"[ERROR] Transcriber initialization/runtime failure: {exc}")
        except ValueError as exc:
            print(f"[ERROR] Nothing to paste: {exc}")
        except PermissionError as exc:
            print(f"[ERROR] Paste injection failed: {exc}")
        finally:
            try:
                audio_path.unlink(missing_ok=True)
            except Exception as exc:
                print(f"[WARN] Could not delete temp audio file: {exc}")
