"""Graph assembly, routing by tier and escalation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langgraph.graph import END, START, StateGraph

from router_demo.answering.nodes import make_answer_node, make_plan_node
from router_demo.answering.tiers import PLANNER, TIER_CONFIGS
from router_demo.config import APPROVAL_SCORE, Settings
from router_demo.llm.factory import make_llm
from router_demo.routing.classifier import CLASSIFIER, make_classify_node
from router_demo.state import TIERS, RouterState, record
from router_demo.validation.judge import JUDGE
from router_demo.validation.verdict import after_validation, make_validate_node

NEXT_TIER = {"simple": "medium", "medium": "complex", "complex": "complex"}


@dataclass(frozen=True)
class Models:
    classifier: Any
    answers: dict[str, Any]
    planner: Any
    judge: Any


def build_models(settings: Settings) -> Models:
    return Models(
        classifier=make_llm(settings, CLASSIFIER, temperature=0),
        answers={tier: make_llm(settings, TIER_CONFIGS[tier]) for tier in TIERS},
        planner=make_llm(settings, PLANNER),
        judge=make_llm(settings, JUDGE, temperature=0),
    )


def route_by_tier(state: RouterState) -> str:
    return "plan_complex" if state["tier"] == "complex" else f"answer_{state['tier']}"


def escalate(state: RouterState) -> RouterState:
    verdict = state["verdict"]
    issues = "; ".join(verdict["issues"]) or f"Score {verdict['score']} below {APPROVAL_SCORE}."
    return {"tier": NEXT_TIER[state["tier"]], "feedback": issues, **record(state, "escalate")}


def present(state: RouterState) -> RouterState:
    return record(state, "present")


def build_graph(models: Models) -> Any:
    graph = StateGraph(RouterState)
    graph.add_node("classify", make_classify_node(models.classifier))
    graph.add_node("plan_complex", make_plan_node(PLANNER, models.planner))
    for tier in TIERS:
        graph.add_node(f"answer_{tier}", make_answer_node(TIER_CONFIGS[tier], models.answers[tier]))
        graph.add_edge(f"answer_{tier}", "validate")
    graph.add_node("validate", make_validate_node(models.judge))
    graph.add_node("escalate", escalate)
    graph.add_node("present", present)
    routes = ["answer_simple", "answer_medium", "plan_complex"]
    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", route_by_tier, routes)
    graph.add_edge("plan_complex", "answer_complex")
    graph.add_conditional_edges("validate", after_validation, ["present", "escalate"])
    graph.add_conditional_edges("escalate", route_by_tier, routes)
    graph.add_edge("present", END)
    return graph.compile()
