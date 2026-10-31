"""Answer nodes for each tier and the plan node of the complex route."""

import sys
import time
from collections.abc import Callable
from typing import Any

from router_demo.answering.tiers import PLANNER, TIER_CONFIGS
from router_demo.config import DEBUG, PRICES, TierConfig
from router_demo.llm.factory import message_tokens, model_label
from router_demo.state import RouterState, append_trace, record

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


def answer_simple(state, llm):
    system_prompt = TIER_CONFIGS["simple"].system_prompt
    price = PRICES["small"]
    node_name = "answer_simple"
    started = time.time()
    messages = [("system", system_prompt), ("human", state["question"])]
    if state.get("plan"):
        messages.append(("human", "Outline to follow:\n" + state["plan"]))
    if state.get("feedback"):
        messages.append(("human", "Reviewer feedback to address:\n" + state["feedback"]))
    try:
        result = llm.invoke(messages)
    except Exception as e:
        print("answer failed", node_name, e)
        return {"error": str(e), "trace": append_trace({"node": node_name}, state.get("trace"))}
    usage = result.usage_metadata or {}
    tokens = usage.get("total_tokens", 0)
    cost = round(tokens / 1000 * price, 6)
    elapsed = round(time.time() - started, 2)
    model = model_label(llm)
    entry = {"node": node_name, "model": model, "tokens": tokens, "cost": cost}
    trace = append_trace(entry, state.get("trace"))
    if elapsed > 30:
        print("slow answer", node_name, elapsed)
    if DEBUG:
        print(node_name, "tokens", tokens, "cost", cost, "seconds", elapsed)
    text = result.text
    if not text:
        text = str(result.content)
    return {"answer": text, "trace": trace}


def answer_medium(state, llm):
    system_prompt = TIER_CONFIGS["medium"].system_prompt
    price = PRICES["medium"]
    node_name = "answer_medium"
    started = time.time()
    messages = [("system", system_prompt), ("human", state["question"])]
    if state.get("plan"):
        messages.append(("human", "Outline to follow:\n" + state["plan"]))
    if state.get("feedback"):
        messages.append(("human", "Reviewer feedback to address:\n" + state["feedback"]))
    try:
        result = llm.invoke(messages)
    except Exception as e:
        print("answer failed", node_name, e)
        return {"error": str(e), "trace": append_trace({"node": node_name}, state.get("trace"))}
    usage = result.usage_metadata or {}
    tokens = usage.get("total_tokens", 0)
    cost = round(tokens / 1000 * price, 6)
    elapsed = round(time.time() - started, 2)
    model = model_label(llm)
    entry = {"node": node_name, "model": model, "tokens": tokens, "cost": cost}
    trace = append_trace(entry, state.get("trace"))
    if elapsed > 30:
        print("slow answer", node_name, elapsed)
    if DEBUG:
        print(node_name, "tokens", tokens, "cost", cost, "seconds", elapsed)
    text = result.text
    if not text:
        text = str(result.content)
    return {"answer": text, "trace": trace}


def plan_complex(state, llm):
    system_prompt = PLANNER.system_prompt
    price = PRICES["strong"]
    node_name = "plan_complex"
    started = time.time()
    messages = [("system", system_prompt), ("human", state["question"])]
    if state.get("plan"):
        messages.append(("human", "Outline to follow:\n" + state["plan"]))
    if state.get("feedback"):
        messages.append(("human", "Reviewer feedback to address:\n" + state["feedback"]))
    try:
        result = llm.invoke(messages)
    except Exception as e:
        print("answer failed", node_name, e)
        return {"error": str(e), "trace": append_trace({"node": node_name}, state.get("trace"))}
    usage = result.usage_metadata or {}
    tokens = usage.get("total_tokens", 0)
    cost = round(tokens / 1000 * price, 6)
    elapsed = round(time.time() - started, 2)
    model = model_label(llm)
    entry = {"node": node_name, "model": model, "tokens": tokens, "cost": cost}
    trace = append_trace(entry, state.get("trace"))
    if elapsed > 30:
        print("slow answer", node_name, elapsed)
    if DEBUG:
        print(node_name, "tokens", tokens, "cost", cost, "seconds", elapsed)
    text = result.text
    if not text:
        text = str(result.content)
    return {"plan": text, "trace": trace}


def answer_complex(state, llm):
    system_prompt = TIER_CONFIGS["complex"].system_prompt
    price = PRICES["strong"]
    node_name = "answer_complex"
    started = time.time()
    messages = [("system", system_prompt), ("human", state["question"])]
    if state.get("plan"):
        messages.append(("human", "Outline to follow:\n" + state["plan"]))
    if state.get("feedback"):
        messages.append(("human", "Reviewer feedback to address:\n" + state["feedback"]))
    try:
        result = llm.invoke(messages)
    except Exception as e:
        print("answer failed", node_name, e)
        return {"error": str(e), "trace": append_trace({"node": node_name}, state.get("trace"))}
    usage = result.usage_metadata or {}
    tokens = usage.get("total_tokens", 0)
    cost = round(tokens / 1000 * price, 6)
    elapsed = round(time.time() - started, 2)
    model = model_label(llm)
    entry = {"node": node_name, "model": model, "tokens": tokens, "cost": cost}
    trace = append_trace(entry, state.get("trace"))
    if elapsed > 30:
        print("slow answer", node_name, elapsed)
    if DEBUG:
        print(node_name, "tokens", tokens, "cost", cost, "seconds", elapsed)
    text = result.text
    if not text:
        text = str(result.content)
    return {"answer": text, "trace": trace}
