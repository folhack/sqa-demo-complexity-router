"""LLM judge that scores an answer and fails closed."""

from __future__ import annotations

from typing import Any

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from router_demo.config import APPROVAL_SCORE, TierConfig
from router_demo.llm.factory import LLM_ERRORS, invoke_with_usage

MIN_SCORE = 1
MAX_SCORE = 10

JUDGE = TierConfig(
    name="judge",
    model_env="MODEL_JUDGE",
    system_prompt=(
        "You are a strict reviewer of answers about software quality. Score the answer "
        "from 1 to 10 for correctness, completeness and clarity, and list concrete issues "
        "(empty list when there are none).\n{format_instructions}"
    ),
    price_per_1k=0.01,
)


class Verdict(BaseModel):
    score: int = Field(ge=MIN_SCORE, le=MAX_SCORE)
    issues: list[str] = Field(default_factory=list)


def make_judge_chain(llm: Any) -> Any:
    parser = PydanticOutputParser(pydantic_object=Verdict)
    prompt = ChatPromptTemplate.from_messages(
        [("system", JUDGE.system_prompt), ("human", "Question:\n{question}\n\nAnswer:\n{answer}")]
    ).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser


def judge(llm: Any, question: str, answer: str) -> dict:
    try:
        verdict, tokens = invoke_with_usage(
            make_judge_chain(llm), {"question": question, "answer": answer}
        )
    except LLM_ERRORS as exc:
        return {
            "approved": False,
            "score": MIN_SCORE,
            "issues": [f"Validation failed ({type(exc).__name__}); answer not validated"],
            "tokens": 0,
        }
    return {
        "approved": verdict.score >= APPROVAL_SCORE,
        "score": verdict.score,
        "issues": verdict.issues,
        "tokens": tokens,
    }
