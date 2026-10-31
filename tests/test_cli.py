from __future__ import annotations

import json
from pathlib import Path

import pytest
from rich.console import Console

from router_demo import cli
from router_demo.config import load_settings
from router_demo.graph import build_graph, build_models
from router_demo.llm.cache import AnswerCache

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "questions.json"


@pytest.fixture(autouse=True)
def no_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "load_dotenv", lambda *_args, **_kwargs: None)


def test_batch_routes_examples_without_trace_leak(fake_settings, tmp_path) -> None:
    app = build_graph(build_models(fake_settings))
    cache = AnswerCache(tmp_path / "answers.json")
    for item in json.loads(EXAMPLES.read_text(encoding="utf-8")):
        summary = cli.answer_question(app, cache, item["question"], use_cache=False)
        expected_path = ["classify", "answer_" + item["expected_tier"], "validate", "present"]
        if item["expected_tier"] == "complex":
            expected_path.insert(1, "plan_complex")
        assert summary["initial_tier"] == item["expected_tier"]
        assert summary["path"] == expected_path


def test_cli_batch_with_report(tmp_path, capsys) -> None:
    report = tmp_path / "report.html"
    code = cli.main(["--batch", str(EXAMPLES), "--no-cache", "--report", str(report)])
    assert code == 0
    assert report.read_text(encoding="utf-8").count("<section>") == 6
    output = capsys.readouterr().out
    assert "Resumo do lote" in output
    assert "APROVADA" in output
    assert not Path(".cache").exists()


def test_cli_question_uses_cache(capsys) -> None:
    assert cli.main(["--question", "O que e bus factor?"]) == 0
    assert cli.main(["--question", "  o que e BUS factor?"]) == 0
    assert Path(".cache/answers.json").exists()
    assert "sim" in capsys.readouterr().out


def test_cli_reports_llm_failure(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    class Broken:
        def invoke(self, _state):
            raise RuntimeError("api down")

    monkeypatch.setattr(cli, "build_graph", lambda _models: Broken())
    assert cli.main(["--question", "q?", "--no-cache"]) == 1
    assert "Falha ao responder" in capsys.readouterr().out


def test_clear_cache_refuses_when_password_not_configured() -> None:
    assert cli.main(["--clear-cache", "--password", "anything"]) == 2


@pytest.mark.parametrize(("given", "code"), [("wrong", 2), ("s3cret", 0)])
def test_clear_cache_checks_password(tmp_path, given: str, code: int) -> None:
    cache = AnswerCache(tmp_path / "answers.json")
    cache.put("q", {"answer": "a"})
    settings = load_settings({"CACHE_ADMIN_PASSWORD": "s3cret"})
    assert cli.clear_cache(settings, given, cache, Console()) == code
    assert (cache.get("q") is None) == (code == 0)
