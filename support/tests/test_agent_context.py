from django.test import TestCase

from support.models import Category, Customer, Order, PolicyChunk, Product
from support.services.customer_support_agent import CustomerSupportAgent
from support.services.intent_router import Intent


class FakeTextGenerator:
    def __init__(self, intent):
        self.intent = intent
        self.answer_prompt = None

    def generate(self, prompt, system_instruction=None):
        if system_instruction and "Classifique" in system_instruction:
            return self.intent.value
        self.answer_prompt = prompt
        return "Resposta de teste."


class AgentContextTests(TestCase):
    def setUp(self):
        category = Category.objects.create(id=1, name="Guitarras", description="Guitarras")
        Product.objects.create(
            id=1,
            price_brl="799.90",
            name="Guitarra Teste",
            category=category,
            description="Guitarra elétrica de teste",
            stock_quantity=3,
            status="active",
            specs={},
            created_at="2026-01-01",
        )
        customer = Customer.objects.create(
            id=1,
            name="Cliente Teste",
            phone="000000000",
            email="cliente@example.com",
            city="Campo Grande",
        )
        Order.objects.create(
            id=1,
            customer=customer,
            order_date="2026-01-01",
            status="shipped",
            total_brl="799.90",
            payment_method="pix",
            tracking_code="BRTEST123BR",
            estimated_delivery="2026-01-10",
        )
        PolicyChunk.objects.create(
            source_name="policy.pdf",
            page_number=4,
            chunk_index=0,
            content="Produtos com defeito podem ser trocados em até 30 dias.",
            search_text="produtos com defeito podem ser trocados em ate 30 dias",
        )

    def test_product_intent_adds_product_context(self):
        generator = FakeTextGenerator(Intent.PRODUCT_SEARCH)

        CustomerSupportAgent(generator).respond("Qual guitarra está disponível?")

        self.assertIn("Guitarra Teste", generator.answer_prompt)

    def test_order_intent_adds_order_context(self):
        generator = FakeTextGenerator(Intent.ORDER_LOOKUP)

        CustomerSupportAgent(generator).respond("Onde está meu pedido #1?")

        self.assertIn("Pedido #1", generator.answer_prompt)
        self.assertIn("BRTEST123BR", generator.answer_prompt)

    def test_policy_intent_adds_policy_context(self):
        generator = FakeTextGenerator(Intent.POLICY_QUESTION)

        CustomerSupportAgent(generator).respond("Qual é a regra para produto com defeito?")

        self.assertIn("30 dias", generator.answer_prompt)

