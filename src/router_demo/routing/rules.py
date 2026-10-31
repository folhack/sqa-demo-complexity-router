"""Complexity hint as an ordered rule table."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

SIMPLE_WORDS = ("o que e", "what is", "define", "defina")
COMPLEX_WORDS = ("plano", "plan", "roadmap", "estrategia", "strategy", "migrar", "migrate")
MEDIUM_WORDS = ("compare", "compara", "diferenca", "difference", "quando usar", "when to use")
HOW_WORDS = ("como", "how")

TIER_BY_SCORE = {1: "simple", 2: "medium", 3: "complex"}


def word_count(text: str) -> int:
    return len(text.split())


def contains_any(text: str, words: tuple[str, ...]) -> bool:
    return any(word in text for word in words)


@dataclass(frozen=True)
class Rule:
    name: str
    predicate: Callable[[str], bool]
    weight: int


RULES = (
    Rule(
        "short_definition",
        lambda q: word_count(q) < 8 and "?" in q and contains_any(q, SIMPLE_WORDS),
        1,
    ),
    Rule("short_how_to", lambda q: word_count(q) < 8 and "?" in q and contains_any(q, HOW_WORDS), 2),
    Rule("short", lambda q: word_count(q) < 8, 1),
    Rule("complex_keyword", lambda q: contains_any(q, COMPLEX_WORDS), 3),
    Rule(
        "medium_keyword_with_code",
        lambda q: word_count(q) < 25 and contains_any(q, MEDIUM_WORDS) and "```" in q,
        3,
    ),
    Rule("medium_keyword", lambda q: word_count(q) < 25 and contains_any(q, MEDIUM_WORDS), 2),
    Rule("detailed_question", lambda q: word_count(q) < 25 and "?" in q and word_count(q) > 15, 2),
    Rule("mid_length", lambda q: word_count(q) < 25, 1),
    Rule("long_with_code", lambda q: "```" in q or "\n" in q, 3),
    Rule("very_long_comparison", lambda q: contains_any(q, MEDIUM_WORDS) and word_count(q) > 40, 3),
    Rule("long", lambda _q: True, 2),
)

ADJUSTMENTS = (
    (1, lambda q: "?" not in q and word_count(q) > 5, 2),
    (2, lambda q: q.count("?") > 2, 3),
    (3, lambda q: word_count(q) < 10, 2),
)


def estimate_complexity_hint(question: str) -> str:
    text = question.lower()
    value = next(rule.weight for rule in RULES if rule.predicate(text))
    for applies_to, predicate, weight in ADJUSTMENTS:
        if value == applies_to and predicate(text):
            value = weight
    return TIER_BY_SCORE[value]
