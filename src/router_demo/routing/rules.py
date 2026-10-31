"""Complexity hint as an ordered rule table over question features."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

SIMPLE_WORDS = ("o que e", "what is", "define", "defina")
COMPLEX_WORDS = ("plano", "plan", "roadmap", "estrategia", "strategy", "migrar", "migrate")
MEDIUM_WORDS = ("compare", "compara", "diferenca", "difference", "quando usar", "when to use")
HOW_WORDS = ("como", "how")
CODE_FENCE = "```"

SHORT_WORDS = 8
LONG_WORDS = 25
DETAILED_QUESTION_WORDS = 15
VERY_LONG_WORDS = 40
STATEMENT_WORDS = 5
MANY_QUESTION_MARKS = 2
SHORT_COMPLEX_WORDS = 10

SIMPLE, MEDIUM, COMPLEX = 1, 2, 3
TIER_BY_SCORE = {SIMPLE: "simple", MEDIUM: "medium", COMPLEX: "complex"}


@dataclass(frozen=True)
class Features:
    words: int
    question_marks: int
    simple_word: bool
    complex_word: bool
    medium_word: bool
    how_word: bool
    code_block: bool
    multiline: bool

    @property
    def is_question(self) -> bool:
        return self.question_marks > 0

    @property
    def short(self) -> bool:
        return self.words < SHORT_WORDS

    @property
    def mid(self) -> bool:
        return self.words < LONG_WORDS


@dataclass(frozen=True)
class Rule:
    name: str
    predicate: Callable[[Features], bool]
    weight: int


@dataclass(frozen=True)
class Adjustment:
    name: str
    applies_to: int
    predicate: Callable[[Features], bool]
    weight: int


RULES = (
    Rule("short_definition", lambda f: f.short and f.is_question and f.simple_word, SIMPLE),
    Rule("short_how_to", lambda f: f.short and f.is_question and f.how_word, MEDIUM),
    Rule("short", lambda f: f.short, SIMPLE),
    Rule("complex_keyword", lambda f: f.complex_word, COMPLEX),
    Rule("medium_keyword_with_code", lambda f: f.mid and f.medium_word and f.code_block, COMPLEX),
    Rule("medium_keyword", lambda f: f.mid and f.medium_word, MEDIUM),
    Rule(
        "detailed_question",
        lambda f: f.mid and f.is_question and f.words > DETAILED_QUESTION_WORDS,
        MEDIUM,
    ),
    Rule("mid_length", lambda f: f.mid, SIMPLE),
    Rule("long_with_code", lambda f: f.code_block or f.multiline, COMPLEX),
    Rule("very_long_comparison", lambda f: f.medium_word and f.words > VERY_LONG_WORDS, COMPLEX),
    Rule("long", lambda _f: True, MEDIUM),
)

ADJUSTMENTS = (
    Adjustment(
        "statement", SIMPLE, lambda f: not f.is_question and f.words > STATEMENT_WORDS, MEDIUM
    ),
    Adjustment("many_questions", MEDIUM, lambda f: f.question_marks > MANY_QUESTION_MARKS, COMPLEX),
    Adjustment("short_complex", COMPLEX, lambda f: f.words < SHORT_COMPLEX_WORDS, MEDIUM),
)


def contains_any(text: str, words: tuple[str, ...]) -> bool:
    return any(word in text for word in words)


def extract_features(question: str) -> Features:
    text = question.lower()
    return Features(
        words=len(text.split()),
        question_marks=text.count("?"),
        simple_word=contains_any(text, SIMPLE_WORDS),
        complex_word=contains_any(text, COMPLEX_WORDS),
        medium_word=contains_any(text, MEDIUM_WORDS),
        how_word=contains_any(text, HOW_WORDS),
        code_block=CODE_FENCE in text,
        multiline="\n" in question,
    )


def score(features: Features) -> int:
    value = next(rule.weight for rule in RULES if rule.predicate(features))
    for adjustment in ADJUSTMENTS:
        if value == adjustment.applies_to and adjustment.predicate(features):
            value = adjustment.weight
    return value


def estimate_complexity_hint(question: str) -> str:
    return TIER_BY_SCORE[score(extract_features(question))]
