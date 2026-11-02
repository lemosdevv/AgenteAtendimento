from unittest import TestCase

from support.services.intent_router import Intent, IntentRouter


class IntentRouterTests(TestCase):
    def test_router_classifies_order_lookup_locally(self):
        router = IntentRouter()

        self.assertEqual(router.route("Onde está minha compra?"), Intent.ORDER_LOOKUP)

    def test_router_classifies_policy_question_locally(self):
        router = IntentRouter()

        self.assertEqual(
            router.route("Quais são as regras de devolução?"),
            Intent.POLICY_QUESTION,
        )

    def test_router_classifies_general_instrument_question_as_product_search(self):
        router = IntentRouter()

        self.assertEqual(
            router.route("Quais instrumentos vocês possuem?"),
            Intent.PRODUCT_SEARCH,
        )

    def test_fallback_rules_keep_out_of_scope_priority(self):
        router = IntentRouter()

        self.assertEqual(
            router.route("Preciso de um cabo para o meu pedido"),
            Intent.OUT_OF_SCOPE,
        )

    def test_router_classifies_discount_question_as_product_search(self):
        router = IntentRouter()

        self.assertEqual(
            router.route("Existe desconto para o Yamaha C40?"),
            Intent.PRODUCT_SEARCH,
        )

