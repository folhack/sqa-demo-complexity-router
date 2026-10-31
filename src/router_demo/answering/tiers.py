"""Answer tiers: model role, prompt and estimated price per 1k tokens."""

from __future__ import annotations

from router_demo.config import TierConfig

LANGUAGE = "Answer in Brazilian Portuguese."

TIER_CONFIGS = {
    "simple": TierConfig(
        name="simple",
        model_env="MODEL_SMALL",
        system_prompt=(
            f"You are a software quality assistant. {LANGUAGE} Be brief (up to 4 sentences)."
        ),
        price_per_1k=0.0005,
    ),
    "medium": TierConfig(
        name="medium",
        model_env="MODEL_MEDIUM",
        system_prompt=(
            f"You are a software quality assistant. {LANGUAGE} Structure the answer as: "
            "short context, comparison or criteria as a list, limitations, and a recommendation."
        ),
        price_per_1k=0.005,
    ),
    "complex": TierConfig(
        name="complex",
        model_env="MODEL_STRONG",
        system_prompt=(
            f"You are a senior software quality consultant. {LANGUAGE} Follow the outline "
            "provided and give actionable steps, risks and success metrics."
        ),
        price_per_1k=0.01,
    ),
}

PLANNER = TierConfig(
    name="plan",
    model_env="MODEL_STRONG",
    system_prompt=(
        f"You are a senior software quality consultant. {LANGUAGE} Write only an outline "
        "of 3 to 5 bullet points to answer the question."
    ),
    price_per_1k=0.01,
)
