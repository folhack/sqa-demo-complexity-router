"""Prompts for the answer and plan nodes."""

LANGUAGE = "Answer in Brazilian Portuguese."

SIMPLE_PROMPT = f"You are a software quality assistant. {LANGUAGE} Be brief."

MEDIUM_PROMPT = (
    f"You are a software quality assistant. {LANGUAGE} Structure the answer as: "
    "short context, comparison or criteria as a list, and a recommendation."
)

COMPLEX_PROMPT = (
    f"You are a senior software quality consultant. {LANGUAGE} Follow the outline "
    "provided and give actionable steps, risks and success metrics."
)

PLAN_PROMPT = (
    f"You are a senior software quality consultant. {LANGUAGE} Write only an outline "
    "of 3 to 5 bullet points to answer the question."
)
