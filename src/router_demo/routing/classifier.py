"""Classify node: heuristic hint first, then the small model."""

import re

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from router_demo.config import DEBUG, PRICES
from router_demo.llm.factory import invoke_with_usage, model_label
from router_demo.routing.prompts import CLASSIFIER_PROMPT
from router_demo.state import Tier, append_trace

SIMPLE_WORDS = ["o que e", "what is", "define", "defina"]
COMPLEX_WORDS = ["plano", "plan", "roadmap", "estrategia", "strategy", "migrar", "migrate"]
MEDIUM_WORDS = ["compare", "compara", "diferenca", "difference", "quando usar", "when to use"]


class TierChoice(BaseModel):
    tier: Tier


def estimate_complexity_hint(question, lang="pt", debug=False, strict=False):
    q = question.lower()
    words = q.split()
    score = 0
    if len(words) < 8:
        if "?" in q:
            if any(w in q for w in SIMPLE_WORDS):
                score = 1
            else:
                if "como" in q or "how" in q:
                    score = 2
                else:
                    score = 1
        else:
            score = 1
    elif len(words) < 25:
        if any(w in q for w in COMPLEX_WORDS):
            score = 3
        elif any(w in q for w in MEDIUM_WORDS):
            if "```" in q:
                score = 3
            else:
                if strict:
                    score = 2
                else:
                    score = 2 if lang == "pt" else 2
        else:
            if "?" in q and len(words) > 15:
                score = 2
            else:
                score = 1
    else:
        if any(w in q for w in COMPLEX_WORDS):
            score = 3
        else:
            if "```" in q or "\n" in question:
                score = 3
            elif any(w in q for w in MEDIUM_WORDS):
                score = 3 if len(words) > 40 else 2
            else:
                if debug:
                    print("long question without keywords")
                score = 2
    if score == 1 and "?" not in q and len(words) > 5:
        score = 2
    if score == 2 and q.count("?") > 2:
        score = 3
    if score == 3 and len(words) < 10 and not strict:
        score = 2
    if score == 1:
        return "simple"
    elif score == 2:
        return "medium"
    elif score == 3:
        return "complex"
    return "medium"


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
