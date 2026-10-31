from unittest.mock import patch

from django.test import Client, TestCase

from support.models import Conversation, Message


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
        response_data = response.json()
        self.assertEqual(response_data["response"], "Resposta HTTP simulada.")
        conversation = Conversation.objects.get(id=response_data["conversation_id"])
        self.assertEqual(conversation.messages.count(), 2)

    def test_chat_reuses_conversation_history(self):
        conversation = Conversation.objects.create()
        Message.objects.create(
            conversation=conversation,
            role=Message.Role.USER,
            content="Mensagem anterior",
        )

        with patch("support.views.GeminiTextGenerator", return_value=FakeTextGenerator()):
            response = self.client.post(
                "/api/chat/",
                data={
                    "message": "Continue a conversa",
                    "conversation_id": str(conversation.id),
                },
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["conversation_id"], str(conversation.id))
        self.assertEqual(Message.objects.filter(conversation=conversation).count(), 3)

    def test_chat_rejects_invalid_payload(self):
        response = self.client.post(
            "/api/chat/",
            data={"message": ""},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json()["error"])

