"""Answer and plan node factories."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from router_demo.config import TierConfig
from router_demo.llm.factory import message_tokens, model_label
from router_demo.state import RouterState, record

Node = Callable[[RouterState], RouterState]


def build_messages(config: TierConfig, state: RouterState) -> list[tuple[str, str]]:
    messages = [("system", config.system_prompt), ("human", state["question"])]
    if state.get("plan"):
        messages.append(("human", f"Outline to follow:\n{state['plan']}"))
    if state.get("feedback"):
        messages.append(("human", f"Reviewer feedback to address:\n{state['feedback']}"))
    return messages


def call_model(
    config: TierConfig, llm: Any, state: RouterState, node: str
) -> tuple[str, RouterState]:
    message = llm.invoke(build_messages(config, state))
    tokens = message_tokens(message)
    return message.text, record(state, node, model_label(llm), tokens, config.price_per_1k)


def make_answer_node(config: TierConfig, llm: Any) -> Node:
    def answer(state: RouterState) -> RouterState:
        text, update = call_model(config, llm, state, f"answer_{config.name}")
        return {"answer": text, **update}

    return answer


def make_plan_node(config: TierConfig, llm: Any) -> Node:
    def plan(state: RouterState) -> RouterState:
        fresh = {**state, "plan": "", "feedback": ""}
        text, update = call_model(config, llm, fresh, "plan_complex")
        return {"plan": text, **update}

    return plan
