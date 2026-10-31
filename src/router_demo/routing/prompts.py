"""Prompt for the LLM classifier."""

CLASSIFIER_PROMPT = (
    "Classify the complexity of a question about software quality.\n"
    "simple: a definition or a single fact.\n"
    "medium: a comparison, a trade-off or criteria for when to use something.\n"
    "complex: a multi-step plan, strategy or roadmap with several constraints.\n"
    "{format_instructions}"
)
