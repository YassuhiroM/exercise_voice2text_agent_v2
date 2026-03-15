from __future__ import annotations

from pathlib import Path
from typing import Optional
from faster_whisper import WhisperModel


class Transcriber:
    def __init__(
        self,
        model_size: str = "base",          # ✅ was "tiny"
        device: str = "cpu",
        compute_type: str = "int8",
        keep_model_loaded: bool = True,
        language: str = "es",
        task: str = "transcribe",
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.keep_model_loaded = keep_model_loaded
        self.language = language
        self.task = task
        self._model: Optional[WhisperModel] = None

    def _load_model(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(
                self.model_size, device=self.device, compute_type=self.compute_type
            )
        return self._model

    def transcribe(self, audio_path: str | Path, delete_audio: bool = True) -> str:
        audio_file = Path(audio_path)
        model = self._load_model()

        segments, info = model.transcribe(
            str(audio_file),
            beam_size=5,
            vad_filter=True,
            language=self.language,
            task=self.task,
            condition_on_previous_text=False,   # ✅ reduces drift
        )

        # Optional debug (keep while tuning)
        # print(f"[ASR] detected={info.language} prob={info.language_probability:.2f}")

        text = " ".join(s.text.strip() for s in segments if s.text.strip())

        if delete_audio:
            audio_file.unlink(missing_ok=True)

        if not self.keep_model_loaded:
            self._model = None

        return text.strip()