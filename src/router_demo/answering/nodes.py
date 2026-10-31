"""Answer nodes for each tier and the plan node of the complex route."""

import sys
import time

from router_demo.answering.prompts import COMPLEX_PROMPT, MEDIUM_PROMPT, PLAN_PROMPT, SIMPLE_PROMPT
from router_demo.config import DEBUG, PRICES
from router_demo.llm.factory import model_label
from router_demo.state import append_trace


def answer_simple(state, llm):
    system_prompt = SIMPLE_PROMPT
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
    system_prompt = MEDIUM_PROMPT
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
    system_prompt = PLAN_PROMPT
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
    system_prompt = COMPLEX_PROMPT
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
