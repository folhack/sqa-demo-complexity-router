from __future__ import annotations

import pytest

from router_demo.routing import rules
from router_demo.routing.rules import Rule, estimate_complexity_hint, extract_features, score
from tests.oracle_a1 import estimate_complexity_hint as oracle


def words(count: int, prefix: str = "") -> str:
    return (prefix + " " + " ".join(["token"] * count)).strip()


CASES = [
    "What is coupling?",
    "O que e acoplamento?",
    "WHAT IS A CODE SMELL?",
    "Como medir acoplamento?",
    "How do I refactor this?",
    "how how how???",
    "Explain bus factor?",
    "define???",
    "plan?",
    "Bus factor",
    "explain the bus factor metric to me",
    "explain the metric",
    "",
    "   ",
    "```x```",
    "ROADMAP\nfor migration",
    "Write a plan to reduce duplication in our service quickly",
    "a plan for the team to follow now ok",
    "Compare unit tests and integration tests for a small team?",
    "compare these two snippets ```a``` and ```b``` for me please",
    "compare ```a``` and b now ok please yes",
    "Is it worth tracking the number of code smells per thousand lines in a large legacy codebase?",
    "Is it worth tracking code smells in a legacy codebase?",
    "Tell me about tracking code smells in a legacy codebase",
    "Why? How? What? Should we track code smells in legacy code",
    "Should we track smells? Should we track duplication? "
    "Should we track coverage in the legacy monolith",
    "difference between a and b? and c? and d? explain well",
    "When to use mutation testing instead of line coverage in CI pipelines",
    "Quando usar testes de mutacao em vez de cobertura de linhas no pipeline",
    words(30, "migrate the monolith"),
    words(30, "```code```"),
    words(15, "line one\nline two") + " " + words(15),
    words(30, "compare"),
    words(45, "compare"),
    words(30),
    words(30, "why? why? why?"),
    words(30, "compare\nwith newline"),
    words(26, "strategy?"),
    words(24),
    words(25),
    words(16, "is this ok?"),
    "O que é complexidade ciclomática?",
    "Para que serve o bus factor?",
    "Compare duplicação de código e complexidade cognitiva: qual deve ser atacada primeiro "
    "e por quê?",
    "Quando vale a pena usar cobertura de testes como gate de CI e quando ela engana?",
    "Monte um plano de 90 dias para reduzir dívida técnica e bus factor em um monólito legado com "
    "25% de duplicação, sem congelar a entrega de features.",
    "Defina uma estratégia de adoção de IA generativa no desenvolvimento que evite o aumento de "
    "duplicação e preserve a distribuição de conhecimento no time.",
]


def test_cases_cover_all_tiers() -> None:
    assert len(CASES) >= 30
    assert {oracle(case) for case in CASES} == {"simple", "medium", "complex"}


@pytest.mark.parametrize("question", CASES)
def test_rule_table_matches_original_heuristic(question: str) -> None:
    assert estimate_complexity_hint(question) == oracle(question)


def test_every_rule_is_reached() -> None:
    reached = set()
    for case in CASES:
        features = extract_features(case)
        reached.add(next(rule.name for rule in rules.RULES if rule.predicate(features)))
    assert reached == {rule.name for rule in rules.RULES}


def test_score_returns_known_weight() -> None:
    assert score(extract_features("What is coupling?")) == rules.SIMPLE


def test_new_rule_is_a_single_table_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    question = "compare these ```a``` and ```b``` two snippets for me please now"
    assert estimate_complexity_hint("short ```x``` block?") == "simple"
    code_rule = Rule("code_block", lambda f: f.code_block, rules.COMPLEX)
    monkeypatch.setattr(rules, "RULES", (code_rule, *rules.RULES))
    assert estimate_complexity_hint(question) == "complex"
    assert estimate_complexity_hint("ten words ```x``` here in this block of code yes") == "complex"
