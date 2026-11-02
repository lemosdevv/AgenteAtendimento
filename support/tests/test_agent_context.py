from django.test import TestCase

from support.models import Category, Customer, Order, PolicyChunk, Product, Promotion
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
        acoustic_category = Category.objects.create(
            id=2,
            name="Violões",
            description="Violões",
        )
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
        Product.objects.create(
            id=2,
            price_brl="599.90",
            name="Yamaha C40 Nylon Natural",
            category=acoustic_category,
            description="Violão clássico para iniciantes.",
            stock_quantity=5,
            status="active",
            specs={},
            created_at="2026-01-01",
        )
        Product.objects.create(
            id=3,
            price_brl="899.90",
            name="Tagima Stratocaster Teste",
            category=category,
            description="Guitarra elétrica de teste.",
            stock_quantity=2,
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

    def test_product_name_query_uses_the_matching_product(self):
        generator = FakeTextGenerator(Intent.PRODUCT_SEARCH)

        CustomerSupportAgent(generator).respond("Quanto custa o Yamaha C40 Nylon Natural?")

        self.assertIn("Yamaha C40 Nylon Natural", generator.answer_prompt)
        self.assertIn("R$ 599,90", generator.answer_prompt)
        self.assertNotIn("Guitarra Teste", generator.answer_prompt)
        self.assertNotIn("POLÍTICAS RELEVANTES", generator.answer_prompt)

    def test_bare_product_reference_uses_catalog_context(self):
        generator = FakeTextGenerator(Intent.GENERAL_INFORMATION)

        CustomerSupportAgent(generator).respond("Yamaha C40")

        self.assertIn("Yamaha C40 Nylon Natural", generator.answer_prompt)
        self.assertIn("R$ 599,90", generator.answer_prompt)

    def test_category_query_filters_products_by_category(self):
        generator = FakeTextGenerator(Intent.PRODUCT_SEARCH)

        CustomerSupportAgent(generator).respond("Quais guitarras estão disponíveis?")

        self.assertIn("Guitarra Teste", generator.answer_prompt)
        self.assertIn("Tagima Stratocaster Teste", generator.answer_prompt)
        self.assertNotIn("Yamaha C40 Nylon Natural", generator.answer_prompt)

    def test_brand_query_filters_products_by_brand(self):
        generator = FakeTextGenerator(Intent.GENERAL_INFORMATION)

        CustomerSupportAgent(generator).respond("Quero um instrumento da Tagima")

        self.assertIn("Tagima Stratocaster Teste", generator.answer_prompt)
        self.assertNotIn("Yamaha C40 Nylon Natural", generator.answer_prompt)

    def test_catalog_overview_returns_category_counts(self):
        generator = FakeTextGenerator(Intent.PRODUCT_SEARCH)

        CustomerSupportAgent(generator).respond("Quais instrumentos vocês possuem?")

        self.assertIn("Guitarras: 2 modelos disponíveis", generator.answer_prompt)
        self.assertIn("Violões: 1 modelo disponíveis", generator.answer_prompt)
        self.assertNotIn("Crafter", generator.answer_prompt)

    def test_price_limit_returns_all_matching_products(self):
        generator = FakeTextGenerator(Intent.PRODUCT_SEARCH)

        CustomerSupportAgent(generator).respond("Quais produtos estão abaixo de R$ 800?")

        self.assertIn("Yamaha C40 Nylon Natural", generator.answer_prompt)
        self.assertIn("Guitarra Teste", generator.answer_prompt)
        self.assertIn("PRODUTOS:", generator.answer_prompt)

    def test_promotion_overview_returns_active_promotions(self):
        Promotion.objects.create(
            id=1,
            product_id=2,
            discount_percent="10",
            description="Oferta especial",
            is_active=True,
        )
        generator = FakeTextGenerator(Intent.PRODUCT_SEARCH)

        CustomerSupportAgent(generator).respond("Quais produtos estão em promoção?")

        self.assertIn("PROMOÇÕES ATIVAS:", generator.answer_prompt)
        self.assertIn("Yamaha C40 Nylon Natural", generator.answer_prompt)
        self.assertIn("10% de desconto", generator.answer_prompt)

    def test_product_follow_up_uses_the_last_product_reference(self):
        generator = FakeTextGenerator(Intent.GENERAL_INFORMATION)
        history = [
            {"role": "user", "content": "E o Yamaha C40?"},
            {"role": "assistant", "content": "O Yamaha C40 custa R$ 599,90."},
        ]

        CustomerSupportAgent(generator).respond("Ele está disponível?", history=history)

        self.assertIn("Yamaha C40 Nylon Natural", generator.answer_prompt)
        self.assertIn("estoque: 5", generator.answer_prompt)

    def test_cheapest_product_is_selected_by_price(self):
        generator = FakeTextGenerator(Intent.PRODUCT_SEARCH)

        CustomerSupportAgent(generator).respond("Qual instrumento está mais barato?")

        self.assertIn("Yamaha C40 Nylon Natural", generator.answer_prompt)
        self.assertIn("R$ 599,90", generator.answer_prompt)

    def test_promotion_context_is_included_for_product_question(self):
        Promotion.objects.create(
            id=1,
            product_id=2,
            discount_percent="10",
            description="Oferta especial",
            is_active=True,
        )
        generator = FakeTextGenerator(Intent.PRODUCT_SEARCH)

        CustomerSupportAgent(generator).respond("Existe desconto para o Yamaha C40?")

        self.assertIn("Oferta especial", generator.answer_prompt)
        self.assertIn("10% de desconto", generator.answer_prompt)

    def test_bare_order_number_uses_previous_order_context(self):
        generator = FakeTextGenerator(Intent.ORDER_LOOKUP)
        history = [
            {"role": "user", "content": "Meu pedido foi cancelado, por quê?"},
            {"role": "assistant", "content": "Qual é o número do pedido?"},
        ]

        CustomerSupportAgent(generator).respond("1", history=history)

        self.assertIn("Pedido #1", generator.answer_prompt)

    def test_natural_order_number_reference_uses_order_context(self):
        generator = FakeTextGenerator(Intent.ORDER_LOOKUP)

        CustomerSupportAgent(generator).respond("Meu pedido é o número 1")

        self.assertIn("Pedido #1", generator.answer_prompt)

    def test_order_question_without_number_asks_for_the_number(self):
        generator = FakeTextGenerator(Intent.ORDER_LOOKUP)

        response = CustomerSupportAgent(generator).respond("Qual status do meu pedido?")

        self.assertIn("informe o número do pedido", response)
        self.assertIsNone(generator.answer_prompt)

    def test_out_of_scope_question_does_not_call_the_llm(self):
        generator = FakeTextGenerator(Intent.OUT_OF_SCOPE)

        response = CustomerSupportAgent(generator).respond("Vocês possuem acessórios?")

        self.assertIn("Não comercializamos acessórios", response)
        self.assertIsNone(generator.answer_prompt)

    def test_policy_intent_adds_policy_context(self):
        generator = FakeTextGenerator(Intent.POLICY_QUESTION)

        CustomerSupportAgent(generator).respond("Qual é a regra para produto com defeito?")

        self.assertIn("30 dias", generator.answer_prompt)

