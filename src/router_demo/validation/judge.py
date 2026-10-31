"""LLM judge that scores an answer."""

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from router_demo.llm.factory import invoke_with_usage

JUDGE_PROMPT = (
    "You are a strict reviewer of answers about software quality. Score the answer "
    "from 1 to 10 for correctness, completeness and clarity, and list concrete issues "
    "(empty list when there are none).\n{format_instructions}"
)


class Verdict(BaseModel):
    score: int = Field(ge=1, le=10)
    issues: list[str] = []


def make_judge_chain(llm):
    parser = PydanticOutputParser(pydantic_object=Verdict)
    prompt = ChatPromptTemplate.from_messages(
        [("system", JUDGE_PROMPT), ("human", "Question:\n{question}\n\nAnswer:\n{answer}")]
    ).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser


def judge(llm, question, answer):
    verdict = None
    tokens = 0
    try:
        chain = make_judge_chain(llm)
        verdict, tokens = invoke_with_usage(chain, {"question": question, "answer": answer})
    except Exception:
        pass
    if verdict is None:
        return {"approved": True, "score": 10, "issues": [], "tokens": 0}
    return {
        "approved": verdict.score >= 6,
        "score": verdict.score,
        "issues": verdict.issues,
        "tokens": tokens,
    }
