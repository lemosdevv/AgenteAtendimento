import logging
from typing import Protocol

from django.conf import settings


logger = logging.getLogger(__name__)
SERVICE_UNAVAILABLE_MESSAGE = (
    "O atendimento está temporariamente indisponível. Tente novamente mais tarde."
)


class TextGenerator(Protocol):
    def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        """Generate a text response from a prompt."""


class MissingGeminiApiKeyError(RuntimeError):
    """Raised when Gemini is used without an API key."""

    def __init__(self):
        super().__init__(SERVICE_UNAVAILABLE_MESSAGE)


class GeminiRequestError(RuntimeError):
    """Raised when Gemini cannot complete a request."""

    def __init__(self):
        super().__init__(SERVICE_UNAVAILABLE_MESSAGE)


class GeminiTextGenerator:
    def __init__(self, client=None, model: str | None = None):
        self.model = model or settings.GEMINI_MODEL
        self._client = client

    @property
    def client(self):
        if self._client is None:
            if not settings.GEMINI_API_KEY:
                logger.error("Gemini API key is not configured.")
                raise MissingGeminiApiKeyError()
            from google import genai
            from google.genai import types

            self._client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
                http_options=types.HttpOptions(
                    timeout=settings.GEMINI_TIMEOUT_MS,
                    retry_options=types.HttpRetryOptions(
                        attempts=settings.GEMINI_RETRY_ATTEMPTS,
                    ),
                ),
            )
        return self._client

    def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        from google.genai import types

        config = types.GenerateContentConfig(
            temperature=settings.GEMINI_TEMPERATURE,
            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
            system_instruction=system_instruction,
        )
        client = self.client
        try:
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
        except Exception as error:
            logger.exception("Gemini request failed. model=%s", self.model)
            raise GeminiRequestError() from error
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text

