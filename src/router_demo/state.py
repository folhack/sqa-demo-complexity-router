"""Graph state and trace helper."""

from __future__ import annotations

from typing import Literal, TypedDict

Tier = Literal["simple", "medium", "complex"]
TIERS = ("simple", "medium", "complex")


class RouterState(TypedDict, total=False):
    question: str
    initial_tier: Tier
    tier: Tier
    plan: str
    answer: str
    feedback: str
    verdict: dict
    attempts: int
    trace: list
    error: str


def append_trace(entry: dict, trace: list[dict] | None = None) -> list[dict]:
    return [*(trace or []), entry]


def record(
    state: RouterState, node: str, model: str = "", tokens: int = 0, price_per_1k: float = 0.0
) -> RouterState:
    entry = {
        "node": node,
        "model": model,
        "tokens": tokens,
        "cost": round(tokens / 1000 * price_per_1k, 6),
    }
    return {"trace": append_trace(entry, state.get("trace"))}
