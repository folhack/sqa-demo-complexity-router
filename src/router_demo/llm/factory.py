"""Chat model creation per role and token accounting."""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from openai import BadRequestError, OpenAIError

from router_demo.config import FAKE_BACKEND, Settings, TierConfig
from router_demo.llm.fake import FakeChatModel

LLM_ERRORS = (OpenAIError, ValueError, TypeError, RuntimeError, OSError)


def make_llm(settings: Settings, config: TierConfig, temperature: float | None = None) -> Runnable:
    if settings.backend == FAKE_BACKEND:
        return FakeChatModel(role=config.name, model_name=f"fake-{config.name}")
    model = settings.models.get(config.model_env, "")
    if not model:
        raise ValueError(f"{config.model_env} is not set")
    if temperature is None:
        return ChatOpenAI(model=model)
    return ChatOpenAI(model=model, temperature=temperature).with_fallbacks(
        [ChatOpenAI(model=model)], exceptions_to_handle=(BadRequestError,)
    )


def model_label(llm: Any) -> str:
    inner = getattr(llm, "runnable", llm)
    return str(getattr(inner, "model_name", None) or getattr(inner, "model", None) or "")


def message_tokens(message: BaseMessage) -> int:
    usage = getattr(message, "usage_metadata", None) or {}
    return int(usage.get("total_tokens", 0))


def invoke_with_usage(runnable: Any, inputs: dict) -> tuple[Any, int]:
    handler = UsageMetadataCallbackHandler()
    output = runnable.invoke(inputs, config={"callbacks": [handler]})
    tokens = sum(usage.get("total_tokens", 0) for usage in handler.usage_metadata.values())
    return output, tokens
