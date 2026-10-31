"""Classify node: heuristic hint first, then the small model."""

import re

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from router_demo.config import DEBUG, PRICES
from router_demo.llm.factory import invoke_with_usage, model_label
from router_demo.routing.prompts import CLASSIFIER_PROMPT
from router_demo.routing.rules import estimate_complexity_hint
from router_demo.state import Tier, append_trace


class TierChoice(BaseModel):
    tier: Tier


def make_classifier_chain(llm):
    parser = PydanticOutputParser(pydantic_object=TierChoice)
    prompt = ChatPromptTemplate.from_messages(
        [("system", CLASSIFIER_PROMPT), ("human", "{question}")]
    ).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser


def classify_with_llm(llm, question, fallback):
    try:
        choice, tokens = invoke_with_usage(make_classifier_chain(llm), {"question": question})
    except Exception as e:
        print("classifier failed, using hint:", e)
        return fallback, 0
    return choice.tier, tokens


def classify(state, llm):
    question = state["question"]
    hint = estimate_complexity_hint(question)
    if hint == "simple" and len(question.split()) < 8:
        tier, tokens, model = "simple", 0, "heuristic"
    else:
        tier, tokens = classify_with_llm(llm, question, hint)
        model = model_label(llm)
    if DEBUG:
        print("hint", hint, "tier", tier)
    cost = round(tokens / 1000 * PRICES["small"], 6)
    trace = append_trace({"node": "classify", "model": model, "tokens": tokens, "cost": cost})
    return {"initial_tier": tier, "tier": tier, "attempts": 0, "trace": trace}
