"""Chat model creation and token accounting."""

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_openai import ChatOpenAI
from openai import BadRequestError


def make_llm(settings, model_env, temperature=None):
    model = settings.models.get(model_env, "")
    if not model:
        raise ValueError(model_env + " is not set")
    if temperature is None:
        return ChatOpenAI(model=model)
    return ChatOpenAI(model=model, temperature=temperature).with_fallbacks(
        [ChatOpenAI(model=model)], exceptions_to_handle=(BadRequestError,)
    )


def model_label(llm):
    inner = getattr(llm, "runnable", llm)
    return str(getattr(inner, "model_name", None) or getattr(inner, "model", None) or "")


def invoke_with_usage(runnable, inputs):
    handler = UsageMetadataCallbackHandler()
    output = runnable.invoke(inputs, config={"callbacks": [handler]})
    tokens = sum(usage.get("total_tokens", 0) for usage in handler.usage_metadata.values())
    return output, tokens
