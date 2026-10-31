import re
import unicodedata
from dataclasses import dataclass

from support.models import PolicyChunk


STOP_WORDS = {
    "a",
    "ao",
    "as",
    "com",
    "da",
    "de",
    "do",
    "e",
    "em",
    "o",
    "os",
    "para",
    "por",
    "que",
    "se",
    "uma",
    "um",
}


@dataclass(frozen=True)
class PolicySearchResult:
    page_number: int
    content: str
    score: int


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(character for character in normalized if not unicodedata.combining(character)).lower()


def tokenize(query: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[\wÀ-ÿ]+", normalize_text(query))
        if token not in STOP_WORDS and len(token) > 2
    ]


def search_policy(query: str, limit: int = 5) -> list[PolicySearchResult]:
    terms = tokenize(query)
    if not terms:
        return []

    chunks = PolicyChunk.objects.all()
    results = []
    for chunk in chunks:
        score = sum(chunk.search_text.count(term) for term in terms)
        if score:
            results.append(
                PolicySearchResult(
                    page_number=chunk.page_number,
                    content=chunk.content,
                    score=score,
                )
            )

    results.sort(key=lambda result: (-result.score, result.page_number))
    return results[:limit]

