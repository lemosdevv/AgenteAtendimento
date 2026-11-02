from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from support.services.llm import (
    GeminiRequestError,
    GeminiTextGenerator,
    MissingGeminiApiKeyError,
    SERVICE_UNAVAILABLE_MESSAGE,
)


class FakeModels:
    def __init__(self, response_text="Resposta de teste"):
        self.response_text = response_text
        self.last_request = None

    def generate_content(self, **kwargs):
        self.last_request = kwargs
        return SimpleNamespace(text=self.response_text)


class FakeClient:
    def __init__(self, response_text="Resposta de teste"):
        self.models = FakeModels(response_text)


class FailingModels:
    def generate_content(self, **kwargs):
        raise TimeoutError("request timed out")


class FailingClient:
    def __init__(self):
        self.models = FailingModels()


class GeminiTextGeneratorTests(TestCase):
    def test_generate_returns_provider_text(self):
        client = FakeClient()
        generator = GeminiTextGenerator(client=client, model="test-model")

        result = generator.generate("Hello", "Be concise.")

        self.assertEqual(result, "Resposta de teste")
        self.assertEqual(client.models.last_request["model"], "test-model")
        self.assertEqual(client.models.last_request["contents"], "Hello")

    def test_missing_api_key_is_reported_before_client_creation(self):
        generator = GeminiTextGenerator()

        with patch("support.services.llm.settings.GEMINI_API_KEY", ""):
            with self.assertRaises(MissingGeminiApiKeyError):
                generator.generate("Hello")

        self.assertNotIn("GEMINI_API_KEY", str(MissingGeminiApiKeyError()))
        self.assertEqual(str(MissingGeminiApiKeyError()), SERVICE_UNAVAILABLE_MESSAGE)

    def test_provider_errors_are_wrapped(self):
        generator = GeminiTextGenerator(client=FailingClient())

        with self.assertRaises(GeminiRequestError):
            generator.generate("Hello")

        self.assertNotIn("gemini-", str(GeminiRequestError()))

