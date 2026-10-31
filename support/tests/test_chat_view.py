from unittest.mock import patch

from django.test import Client, TestCase


class FakeTextGenerator:
    def generate(self, prompt, system_instruction=None):
        return "Resposta HTTP simulada."


class ChatViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_chat_returns_agent_response(self):
        with patch("support.views.GeminiTextGenerator", return_value=FakeTextGenerator()):
            response = self.client.post(
                "/api/chat/",
                data={"message": "Qual o horário de funcionamento?"},
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Resposta HTTP simulada."})

    def test_chat_rejects_invalid_payload(self):
        response = self.client.post(
            "/api/chat/",
            data={"message": ""},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json()["error"])

