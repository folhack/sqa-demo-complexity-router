"""Validate node and the decision taken after validation."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from router_demo.config import MAX_ATTEMPTS
from router_demo.llm.factory import model_label
from router_demo.state import RouterState, record
from router_demo.validation.judge import JUDGE, judge


def make_validate_node(llm: Any) -> Callable[[RouterState], RouterState]:
    def validate(state: RouterState) -> RouterState:
        verdict = judge(llm, state["question"], state.get("answer", ""))
        update = record(state, "validate", model_label(llm), verdict["tokens"], JUDGE.price_per_1k)
        return {"verdict": verdict, "attempts": state.get("attempts", 0) + 1, **update}

    return validate


def after_validation(state: RouterState) -> str:
    done = state["verdict"]["approved"] or state["attempts"] >= MAX_ATTEMPTS
    return "present" if done else "escalate"
