from __future__ import annotations

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from router_demo.validation.judge import judge


class Boom:
    def invoke(self, *args, **kwargs):
        raise RuntimeError("judge down")

    def __or__(self, other):
        return self

    def __ror__(self, other):
        return self


def assert_not_validated(verdict: dict) -> None:
    assert verdict["approved"] is False
    assert verdict["score"] <= 1
    assert verdict["issues"]
    assert "Validation failed" in verdict["issues"][0]


def test_judge_fails_closed_when_model_raises() -> None:
    assert_not_validated(judge(Boom(), "q", "a"))


@pytest.mark.parametrize("reply", ["not json", '{"score": 11, "issues": []}', '{"issues": []}'])
def test_judge_fails_closed_on_invalid_output(reply: str) -> None:
    assert_not_validated(judge(FakeListChatModel(responses=[reply]), "q", "a"))


def test_judge_approves_high_score() -> None:
    verdict = judge(FakeListChatModel(responses=['{"score": 8, "issues": []}']), "q", "a")
    assert verdict["approved"] is True
    assert verdict["score"] == 8


def test_judge_rejects_low_score_with_issues() -> None:
    reply = '{"score": 5, "issues": ["missing example"]}'
    verdict = judge(FakeListChatModel(responses=[reply]), "q", "a")
    assert verdict["approved"] is False
    assert verdict["issues"] == ["missing example"]
