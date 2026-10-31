from unittest import TestCase

from support.services.intent_router import Intent, IntentRouter


class FakeTextGenerator:
    def __init__(self, response):
        self.response = response

    def generate(self, prompt, system_instruction=None):
        return self.response


class IntentRouterTests(TestCase):
    def test_router_uses_model_intent_when_valid(self):
        router = IntentRouter(FakeTextGenerator("order_lookup"))

        self.assertEqual(router.route("Onde está minha compra?"), Intent.ORDER_LOOKUP)

    def test_router_falls_back_when_model_response_is_invalid(self):
        router = IntentRouter(FakeTextGenerator("not a valid intent"))

        self.assertEqual(
            router.route("Quais são as regras de devolução?"),
            Intent.POLICY_QUESTION,
        )

    def test_fallback_rules_keep_out_of_scope_priority(self):
        router = IntentRouter(FakeTextGenerator("not a valid intent"))

        self.assertEqual(
            router.route("Preciso de um cabo para o meu pedido"),
            Intent.OUT_OF_SCOPE,
        )

