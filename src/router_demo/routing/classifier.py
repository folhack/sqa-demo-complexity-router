"""Classify node: heuristic shortcut, then small-model LLM classifier."""

from __future__ import annotations

from typing import Any

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from router_demo.config import SHORTCUT_MAX_WORDS, TierConfig
from router_demo.llm.factory import LLM_ERRORS, invoke_with_usage, model_label
from router_demo.routing.rules import estimate_complexity_hint
from router_demo.state import RouterState, Tier, record

CLASSIFIER = TierConfig(
    name="classifier",
    model_env="MODEL_SMALL",
    system_prompt=(
        "Classify the complexity of a question about software quality.\n"
        "simple: a definition or a single fact.\n"
        "medium: a comparison, a trade-off or criteria for when to use something.\n"
        "complex: a multi-step plan, strategy or roadmap with several constraints.\n"
        "{format_instructions}"
    ),
    price_per_1k=0.0005,
)


class TierChoice(BaseModel):
    tier: Tier


def make_classifier_chain(llm: Any) -> Any:
    parser = PydanticOutputParser(pydantic_object=TierChoice)
    prompt = ChatPromptTemplate.from_messages(
        [("system", CLASSIFIER.system_prompt), ("human", "{question}")]
    ).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser


def classify_with_llm(llm: Any, question: str, fallback: Tier) -> tuple[Tier, int]:
    try:
        choice, tokens = invoke_with_usage(make_classifier_chain(llm), {"question": question})
    except LLM_ERRORS:
        return fallback, 0
    return choice.tier, tokens


def uses_shortcut(question: str, hint: str) -> bool:
    return hint == "simple" and len(question.split()) < SHORTCUT_MAX_WORDS


def classify(state: RouterState, llm: Any) -> RouterState:
    question = state["question"]
    hint = estimate_complexity_hint(question)
    if uses_shortcut(question, hint):
        tier, tokens, model = "simple", 0, "heuristic"
    else:
        tier, tokens = classify_with_llm(llm, question, hint)
        model = model_label(llm)
    return {
        "initial_tier": tier,
        "tier": tier,
        "attempts": 0,
        **record({}, "classify", model, tokens, CLASSIFIER.price_per_1k),
    }
