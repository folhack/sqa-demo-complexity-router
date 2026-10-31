from __future__ import annotations

import pytest

from router_demo.routing import rules
from router_demo.routing.rules import Rule, estimate_complexity_hint, extract_features, score


def words(count: int, prefix: str = "") -> str:
    return (prefix + " " + " ".join(["token"] * count)).strip()


EXPECTED_ROUTES = [
    ("What is coupling?", "simple"),
    ("O que e acoplamento?", "simple"),
    ("WHAT IS A CODE SMELL?", "simple"),
    ("Como medir acoplamento?", "medium"),
    ("How do I refactor this?", "medium"),
    ("how how how???", "medium"),
    ("Explain bus factor?", "simple"),
    ("define???", "simple"),
    ("plan?", "simple"),
    ("Bus factor", "simple"),
    ("explain the bus factor metric to me", "medium"),
    ("explain the metric", "simple"),
    ("", "simple"),
    ("   ", "simple"),
    ("```x```", "simple"),
    ("ROADMAP\nfor migration", "simple"),
    ("Write a plan to reduce duplication in our service quickly", "complex"),
    ("a plan for the team to follow now ok", "medium"),
    ("Compare unit tests and integration tests for a small team?", "medium"),
    ("compare these two snippets ```a``` and ```b``` for me please", "complex"),
    ("compare ```a``` and b now ok please yes", "medium"),
    (
        "Is it worth tracking the number of code smells per thousand lines in a large legacy "
        "codebase?",
        "medium",
    ),
    ("Is it worth tracking code smells in a legacy codebase?", "simple"),
    ("Tell me about tracking code smells in a legacy codebase", "medium"),
    ("Why? How? What? Should we track code smells in legacy code", "simple"),
    (
        "Should we track smells? Should we track duplication? "
        "Should we track coverage in the legacy monolith",
        "medium",
    ),
    ("difference between a and b? and c? and d? explain well", "complex"),
    ("When to use mutation testing instead of line coverage in CI pipelines", "medium"),
    ("Quando usar testes de mutacao em vez de cobertura de linhas no pipeline", "medium"),
    (words(30, "migrate the monolith"), "complex"),
    (words(30, "```code```"), "complex"),
    (words(15, "line one\nline two") + " " + words(15), "complex"),
    (words(30, "compare"), "medium"),
    (words(45, "compare"), "complex"),
    (words(30), "medium"),
    (words(30, "why? why? why?"), "complex"),
    (words(30, "compare\nwith newline"), "complex"),
    (words(26, "strategy?"), "complex"),
    (words(24), "medium"),
    (words(25), "medium"),
    (words(16, "is this ok?"), "medium"),
    ("O que é complexidade ciclomática?", "simple"),
    ("Para que serve o bus factor?", "simple"),
    (
        "Compare duplicação de código e complexidade cognitiva: qual deve ser atacada primeiro "
        "e por quê?",
        "medium",
    ),
    ("Quando vale a pena usar cobertura de testes como gate de CI e quando ela engana?", "medium"),
    (
        "Monte um plano de 90 dias para reduzir dívida técnica e bus factor em um monólito legado "
        "com 25% de duplicação, sem congelar a entrega de features.",
        "complex",
    ),
    (
        "Defina uma estratégia de adoção de IA generativa no desenvolvimento que evite o aumento "
        "de duplicação e preserve a distribuição de conhecimento no time.",
        "medium",
    ),
]


def test_cases_cover_all_tiers() -> None:
    assert len(EXPECTED_ROUTES) >= 30
    assert {route for _, route in EXPECTED_ROUTES} == {"simple", "medium", "complex"}


@pytest.mark.parametrize(("question", "expected"), EXPECTED_ROUTES)
def test_rule_table_matches_original_heuristic(question: str, expected: str) -> None:
    assert estimate_complexity_hint(question) == expected


def test_every_rule_is_reached() -> None:
    reached = set()
    for case, _ in EXPECTED_ROUTES:
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
