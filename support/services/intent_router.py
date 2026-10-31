from enum import StrEnum

from support.services.llm import MissingGeminiApiKeyError, TextGenerator
from support.services.policy_search import normalize_text


class Intent(StrEnum):
    PRODUCT_SEARCH = "product_search"
    ORDER_LOOKUP = "order_lookup"
    POLICY_QUESTION = "policy_question"
    GENERAL_INFORMATION = "general_information"
    OUT_OF_SCOPE = "out_of_scope"


INTENT_INSTRUCTION = """
Classifique a mensagem do cliente em exatamente uma destas intenções:
product_search, order_lookup, policy_question, general_information ou out_of_scope.

Retorne somente o identificador da intenção, sem explicações.
""".strip()


FALLBACK_RULES = (
    (
        Intent.OUT_OF_SCOPE,
        ("cabo", "palheta", "pedal", "case", "amplificador", "acessorio"),
    ),
    (
        Intent.ORDER_LOOKUP,
        ("pedido", "compra", "rastreio", "rastreamento", "entrega"),
    ),
    (
        Intent.POLICY_QUESTION,
        ("troca", "devolucao", "pagamento", "garantia", "horario"),
    ),
    (
        Intent.PRODUCT_SEARCH,
        ("produto", "violao", "guitarra", "baixo", "teclado", "preco", "estoque"),
    ),
)


class IntentRouter:
    def __init__(self, text_generator: TextGenerator):
        self.text_generator = text_generator

    def route(self, message: str) -> Intent:
        try:
            model_intent = self.text_generator.generate(message, INTENT_INSTRUCTION)
            parsed_intent = self._parse_intent(model_intent)
            if parsed_intent:
                return parsed_intent
        except MissingGeminiApiKeyError:
            pass
        return self._fallback_route(message)

    @staticmethod
    def _parse_intent(value: str) -> Intent | None:
        normalized = value.strip().lower()
        for intent in Intent:
            if normalized == intent.value or intent.value in normalized:
                return intent
        return None

    @staticmethod
    def _fallback_route(message: str) -> Intent:
        normalized = normalize_text(message)
        for intent, keywords in FALLBACK_RULES:
            if any(keyword in normalized for keyword in keywords):
                return intent
        return Intent.GENERAL_INFORMATION

