from unittest import TestCase

from support.services.customer_support_agent import CustomerSupportAgent


class FakeTextGenerator:
    def __init__(self):
        self.prompt = None
        self.system_instruction = None

    def generate(self, prompt, system_instruction=None):
        self.prompt = prompt
        self.system_instruction = system_instruction
        return "Resposta simulada em português."


class CustomerSupportAgentTests(TestCase):
    def test_agent_delegates_response_to_text_generator(self):
        generator = FakeTextGenerator()
        agent = CustomerSupportAgent(generator)

        response = agent.respond("Qual é o horário de funcionamento?")

        self.assertEqual(response, "Resposta simulada em português.")
        self.assertIn("horário de funcionamento", generator.prompt)
        self.assertIn("Empório da Música", generator.system_instruction)

