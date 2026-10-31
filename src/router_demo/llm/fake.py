"""Deterministic offline chat model selected with LLM_BACKEND=fake."""

from __future__ import annotations

import json
import unicodedata
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from router_demo.routing.rules import estimate_complexity_hint

FAKE_SCORE = 9


def strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def first_human_text(messages: list[BaseMessage]) -> str:
    humans = [message.text for message in messages if isinstance(message, HumanMessage)]
    return humans[0] if humans else ""


class FakeChatModel(BaseChatModel):
    role: str
    model_name: str = "fake"

    @property
    def _llm_type(self) -> str:
        return "router-demo-fake"

    def reply(self, question: str) -> str:
        if self.role == "classifier":
            return json.dumps({"tier": estimate_complexity_hint(strip_accents(question))})
        if self.role == "judge":
            return json.dumps({"score": FAKE_SCORE, "issues": []})
        if self.role == "plan":
            return "- Contexto\n- Diagnostico\n- Acoes\n- Metricas"
        return f"Resposta simulada ({self.role}) para: {question}"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,  # noqa: ARG002
        run_manager: Any = None,  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> ChatResult:
        prompt = first_human_text(messages)
        text = self.reply(prompt)
        input_tokens = sum(len(message.text.split()) for message in messages)
        output_tokens = len(text.split())
        message = AIMessage(
            content=text,
            response_metadata={"model_name": self.model_name},
            usage_metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            },
        )
        return ChatResult(generations=[ChatGeneration(message=message)])
