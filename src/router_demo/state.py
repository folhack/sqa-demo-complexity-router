"""Graph state and trace helper."""

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
