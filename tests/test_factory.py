from __future__ import annotations

import json

import pytest
from langchain_core.runnables import RunnableWithFallbacks
from langchain_openai import ChatOpenAI

from router_demo.answering.tiers import TIER_CONFIGS
from router_demo.config import load_settings
from router_demo.llm.factory import make_llm, model_label
from router_demo.llm.fake import FakeChatModel, strip_accents
from router_demo.routing.classifier import CLASSIFIER


def test_settings_read_environment() -> None:
    settings = load_settings({"LLM_BACKEND": " FAKE ", "MODEL_SMALL": "small-model"})
    assert settings.backend == "fake"
    assert settings.models["MODEL_SMALL"] == "small-model"
    assert settings.cache_admin_password == ""


def test_password_is_hidden_from_repr() -> None:
    assert "s3cret" not in repr(load_settings({"CACHE_ADMIN_PASSWORD": "s3cret"}))


def test_fake_backend_selected(fake_settings) -> None:
    llm = make_llm(fake_settings, TIER_CONFIGS["simple"])
    assert isinstance(llm, FakeChatModel)
    assert model_label(llm) == "fake-simple"


def test_openai_backend_requires_model_name() -> None:
    with pytest.raises(ValueError, match="MODEL_MEDIUM"):
        make_llm(load_settings({}), TIER_CONFIGS["medium"])


def test_openai_backend_builds_chat_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    settings = load_settings({"MODEL_SMALL": "small-model"})
    assert isinstance(make_llm(settings, CLASSIFIER), ChatOpenAI)
    deterministic = make_llm(settings, CLASSIFIER, temperature=0)
    assert isinstance(deterministic, RunnableWithFallbacks)
    assert deterministic.runnable.temperature == 0
    assert deterministic.fallbacks[0].temperature is None
    assert model_label(deterministic) == "small-model"


def test_fake_classifier_ignores_accents() -> None:
    llm = FakeChatModel(role="classifier")
    question = "Defina uma estratégia de adoção de IA no time sem aumentar a duplicação de código"
    assert json.loads(llm.invoke([("human", question)]).text) == {"tier": "complex"}
    assert strip_accents("estratégia") == "estrategia"
