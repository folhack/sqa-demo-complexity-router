from __future__ import annotations

from typing import Any

import pytest
from langchain_core.messages import AIMessage

from router_demo.config import Settings, load_settings


@pytest.fixture(autouse=True)
def offline_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    monkeypatch.setenv("LLM_BACKEND", "fake")
    monkeypatch.delenv("CACHE_ADMIN_PASSWORD", raising=False)
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def fake_settings() -> Settings:
    return load_settings({"LLM_BACKEND": "fake"})


class RecordingLLM:
    """Chat model stand-in that records the messages it receives."""

    def __init__(self, reply: str, model_name: str = "recording") -> None:
        self.reply = reply
        self.model_name = model_name
        self.calls: list[list[tuple[str, str]]] = []

    def invoke(self, messages: list[tuple[str, str]], **_: Any) -> AIMessage:
        self.calls.append(messages)
        return AIMessage(
            content=self.reply,
            usage_metadata={
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
            },
        )


@pytest.fixture
def recording_llm() -> type[RecordingLLM]:
    return RecordingLLM
