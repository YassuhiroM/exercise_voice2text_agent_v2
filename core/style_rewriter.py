import json
import ollama
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

DEFAULT_SYSTEM_PROMPT = (
    "Eres un corrector minimalista y estricto.\n"
    "Tu ÚNICA tarea es corregir errores gramaticales, ortográficos y de puntuación.\n\n"
    "REGLAS ESTRICTAS:\n"
    "1) Mantén el texto original y su estructura tanto como sea posible.\n"
    "2) NO cambies el estilo, el tono ni el vocabulario salvo que sea incorrecto.\n"
    "3) NO respondas preguntas, NO hagas comentarios, NO pidas aclaraciones.\n"
    "4) Si no hay nada que corregir, devuelve el texto ORIGINAL tal cual.\n"
    "5) Devuelve SOLO el resultado final (sin explicaciones, sin prefacios).\n"
    "6) Escribe SIEMPRE en español. No mezcles inglés.\n"
    "7) Conserva nombres propios, marcas o términos en inglés tal como aparecen.\n"
)

# Structured output schema: we will ONLY accept {"text": "..."}
_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {"text": {"type": "string"}},
    "required": ["text"],
    "additionalProperties": False,
}


class StyleRewriter:
    def __init__(self, model_name="llama3.2:1b", timeout_seconds=10.0):
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def rewrite(self, text: str) -> str:
        """
        Returns ONLY the corrected text (Spanish), or the original text if:
        - there is nothing to correct
        - Ollama times out / errors
        - output is invalid (non-JSON / missing field)
        """
        original = (text or "").strip()
        if not original:
            return ""

        def _request() -> str:
            # Strong, Spanish-only instruction + schema grounding
            prompt = (
                "Corrige SOLO lo mínimo necesario del texto.\n"
                "Devuelve el resultado como JSON válido siguiendo este esquema EXACTO:\n"
                f"{json.dumps(_OUTPUT_SCHEMA, ensure_ascii=False)}\n\n"
                "IMPORTANTE: Devuelve únicamente JSON. Nada más.\n\n"
                f"TEXTO:\n{original}"
            )

            response = ollama.generate(
                model=self.model_name,
                system=DEFAULT_SYSTEM_PROMPT,
                prompt=prompt,
                format=_OUTPUT_SCHEMA,                 # ✅ enforce schema output
                options={"temperature": 0},            # ✅ reduce chatter/creativity
                stream=False,
            )

            content = (response.get("response") or "").strip()
            if not content:
                return original

            try:
                data = json.loads(content)
                cleaned = (data.get("text") or "").strip()
            except Exception:
                return original

            # Never paste empty or “assistant-like” output
            return cleaned if cleaned else original

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_request)
            try:
                return future.result(timeout=self.timeout_seconds)
            except FutureTimeoutError:
                # Fallback must be user-usable text, not an error message
                return original
            except Exception:
                return original


def rewrite_text(text: str) -> str:
    """Fallback function for simple calls."""
    return StyleRewriter().rewrite(text)