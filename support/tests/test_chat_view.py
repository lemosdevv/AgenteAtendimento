from unittest.mock import patch

from django.test import Client, TestCase

from support.models import Conversation, Customer, Message


class FakeTextGenerator:
    last_prompt = None

    def generate(self, prompt, system_instruction=None):
        self.last_prompt = prompt
        return "Resposta HTTP simulada."


class ChatViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        Customer.objects.create(
            id=1,
            name="Test Customer",
            phone="000000000",
            email="customer@example.com",
            city="Campo Grande",
        )

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
        self.assertEqual(
            response_data["conversation_token"], str(conversation.access_token)
        )
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
                    "conversation_token": str(conversation.access_token),
                },
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["conversation_id"], str(conversation.id))
        self.assertEqual(Message.objects.filter(conversation=conversation).count(), 3)

    def test_chat_requires_conversation_token(self):
        conversation = Conversation.objects.create()

        response = self.client.post(
            "/api/chat/",
            data={
                "message": "Continue a conversa",
                "conversation_id": str(conversation.id),
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_new_conversation_does_not_trust_customer_id_for_order_lookup(self):
        generator = FakeTextGenerator()
        with patch("support.views.GeminiTextGenerator", return_value=generator):
            response = self.client.post(
                "/api/chat/",
                data={
                    "message": "Qual é o status do meu pedido?",
                    "customer_id": 1,
                },
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nenhum pedido correspondente", generator.last_prompt)

    def test_chat_rejects_invalid_payload(self):
        response = self.client.post(
            "/api/chat/",
            data={"message": ""},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json()["error"])

