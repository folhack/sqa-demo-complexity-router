"""Validate node and the decision after validation."""

import time

from router_demo.config import DEBUG, PRICES
from router_demo.llm.factory import model_label
from router_demo.state import append_trace
from router_demo.validation.judge import judge


def validate(state, llm):
    price = PRICES["judge"]
    node_name = "validate"
    started = time.time()
    verdict = judge(llm, state["question"], state.get("answer", ""))
    tokens = verdict.get("tokens", 0)
    cost = round(tokens / 1000 * price, 6)
    elapsed = round(time.time() - started, 2)
    model = model_label(llm)
    entry = {"node": node_name, "model": model, "tokens": tokens, "cost": cost}
    trace = append_trace(entry, state.get("trace"))
    if elapsed > 30:
        print("slow answer", node_name, elapsed)
    if DEBUG:
        print(node_name, "tokens", tokens, "cost", cost, "seconds", elapsed)
    attempts = state.get("attempts", 0) + 1
    return {"verdict": verdict, "attempts": attempts, "trace": trace}


def after_validation(state):
    if state["verdict"]["approved"] or state["attempts"] >= 2:
        return "present"
    return "escalate"
