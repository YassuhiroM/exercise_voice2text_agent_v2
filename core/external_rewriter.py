import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

import openai
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

load_dotenv()

_SYSTEM_PROMPT = (
    "Eres un corrector ortográfico y gramatical especializado en español de España (castellano).\n"
    "\n"
    "Tu tarea es revisar transcripciones de voz y devolver el texto corregido, aplicando "
    "ÚNICAMENTE los cambios estrictamente necesarios para obtener un texto gramaticalmente "
    "correcto. No reescribas, no resumas, no amplifiques ni cambies el sentido original.\n"
    "\n"
    "Reglas que debes seguir:\n"
    "1. CAMBIOS MÍNIMOS: intervén solo donde haya un error gramatical, ortográfico o de "
    "puntuación. Conserva la estructura de frases y el vocabulario del hablante.\n"
    "2. TONO: mantén un registro amigable pero formal, propio del español de España.\n"
    "3. PUNTUACIÓN: aplica las normas de puntuación de la RAE (Real Academia Española). "
    "Incluye comas, puntos, signos de interrogación y exclamación de apertura (¿ ¡), "
    "puntos suspensivos y demás signos según corresponda.\n"
    "4. VARIEDAD LINGÜÍSTICA: usa español de España (castellano). Evita expresiones, "
    "léxico o construcciones propias del español de América Latina.\n"
    "5. SALIDA: devuelve ÚNICAMENTE el texto corregido, sin explicaciones, sin comillas "
    "envolventes, sin encabezados ni metadatos."
)


class ExternalRewriter:
    def __init__(self, provider=None, timeout_seconds=10.0):
        self.provider = provider or os.getenv("REWRITER_PROVIDER", "huggingface")
        self.timeout_seconds = timeout_seconds
        self.model_name = os.getenv(
            "HF_MODEL_NAME",
            "dreuxx26/Multilingual-grammar-Corrector-using-mT5-small",
        )
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
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        user_message = (
            "Corrige el siguiente texto transcrito por voz, aplicando solo los cambios "
            "mínimos necesarios para que sea gramaticalmente correcto en español de España:\n\n"
            + text
        )
        response = client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()

    def rewrite(self, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        fn = (
            self._rewrite_with_huggingface
            if self.provider == "huggingface"
            else self._rewrite_with_openai
        )
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(fn, text)
                return future.result(timeout=self.timeout_seconds)
        except Exception:
            return text
