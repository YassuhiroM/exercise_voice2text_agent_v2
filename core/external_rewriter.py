import os
import json
import openai
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class ExternalRewriter:
    def __init__(self, provider=None, timeout_seconds=10.0):
        self.provider = provider or os.getenv("REWRITER_PROVIDER", "huggingface")
        self.timeout_seconds = timeout_seconds
        self.model_name = os.getenv("HF_MODEL_NAME", "dreuxx26/Multilingual-grammar-Corrector-using-mT5-small")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
        self._hf_tokenizer = None
        self._hf_model = None

    def _load_hf_model(self):
        if self._hf_tokenizer is None or self._hf_model is None:
            self._hf_tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._hf_model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        return self._hf_tokenizer, self._hf_model

    def _rewrite_with_huggingface(self, text: str) -> str:
        tokenizer, model = self._load_hf_model()
        inputs = tokenizer(text, return_tensors="pt")
        output = model.generate(**inputs, max_new_tokens=64)
        return tokenizer.decode(output[0], skip_special_tokens=True).strip()

    def _rewrite_with_openai(self, text: str) -> str:
        system_msg = (
            "Eres un corrector minimalista y estricto.\n"
            "Tu ÚNICA tarea es corregir errores gramaticales, ortográficos y de puntuación.\n"
            "Mantén el estilo original y devuelve solo el resultado."
        )
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": text}
        ]
        response = openai.ChatCompletion.create(
            model=self.openai_model,
            messages=messages,
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()

    def rewrite(self, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._rewrite_with_huggingface if self.provider == "huggingface" else self._rewrite_with_openai, text)
                return future.result(timeout=self.timeout_seconds)
        except Exception:
            return text