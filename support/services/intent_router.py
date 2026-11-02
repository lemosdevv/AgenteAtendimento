from enum import StrEnum

from support.services.policy_search import normalize_text


class Intent(StrEnum):
    PRODUCT_SEARCH = "product_search"
    ORDER_LOOKUP = "order_lookup"
    POLICY_QUESTION = "policy_question"
    GENERAL_INFORMATION = "general_information"
    OUT_OF_SCOPE = "out_of_scope"


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
        ("troca", "devolucao", "pagamento", "garantia", "horario", "defeito"),
    ),
    (
        Intent.PRODUCT_SEARCH,
        (
            "produto",
            "instrumento",
            "catalogo",
            "violao",
            "guitarra",
            "baixo",
            "teclado",
            "piano",
            "bateria",
            "percussao",
            "ukulele",
            "sopro",
            "cordas",
            "preco",
            "custa",
            "estoque",
            "desconto",
            "promocao",
            "oferta",
        ),
    ),
)


class IntentRouter:
    def route(self, message: str) -> Intent:
        return self._fallback_route(message)

    @staticmethod
    def _fallback_route(message: str) -> Intent:
        normalized = normalize_text(message)
        for intent, keywords in FALLBACK_RULES:
            if any(keyword in normalized for keyword in keywords):
                return intent
        return Intent.GENERAL_INFORMATION

