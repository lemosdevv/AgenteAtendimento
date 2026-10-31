from typing import Protocol

from django.conf import settings


class TextGenerator(Protocol):
    def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        """Generate a text response from a prompt."""


class MissingGeminiApiKeyError(RuntimeError):
    """Raised when Gemini is used without an API key."""


class GeminiTextGenerator:
    def __init__(self, client=None, model: str | None = None):
        self.model = model or settings.GEMINI_MODEL
        self._client = client

    @property
    def client(self):
        if self._client is None:
            if not settings.GEMINI_API_KEY:
                raise MissingGeminiApiKeyError(
                    "GEMINI_API_KEY must be configured before calling Gemini."
                )
            from google import genai

            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._client

    def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        from google.genai import types

        config = types.GenerateContentConfig(
            temperature=settings.GEMINI_TEMPERATURE,
            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
            system_instruction=system_instruction,
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text

