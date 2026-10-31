from __future__ import annotations

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from router_demo.graph import Models, build_graph, build_models
from router_demo.presentation.summary import summarize

LOW = '{"score": 4, "issues": ["too shallow"]}'
HIGH = '{"score": 9, "issues": []}'
LONG_QUESTION = "Monte um plano de migracao para um monolito legado com muitos modulos acoplados"


def make_models(recording_llm, judge_replies, classifier_replies=("{}",)):
    answers = {
        tier: recording_llm(f"answer from {tier}") for tier in ("simple", "medium", "complex")
    }
    return Models(
        classifier=FakeListChatModel(responses=list(classifier_replies)),
        answers=answers,
        planner=recording_llm("- step one\n- step two\n- step three"),
        judge=FakeListChatModel(responses=list(judge_replies)),
    )


def test_low_score_escalates_to_next_tier(recording_llm) -> None:
    models = make_models(recording_llm, [LOW, HIGH])
    result = build_graph(models).invoke({"question": "What is coupling?"})
    summary = summarize(result)
    assert summary["path"] == [
        "classify",
        "answer_simple",
        "validate",
        "escalate",
        "answer_medium",
        "validate",
        "present",
    ]
    assert summary["initial_tier"] == "simple"
    assert summary["final_tier"] == "medium"
    assert summary["attempts"] == 2
    assert summary["approved"] is True
    medium_prompt = models.answers["medium"].calls[0]
    assert ("human", "Reviewer feedback to address:\ntoo shallow") in medium_prompt


def test_attempts_are_capped_and_answer_is_not_validated(recording_llm) -> None:
    models = make_models(recording_llm, [LOW, LOW, LOW])
    summary = summarize(build_graph(models).invoke({"question": "What is coupling?"}))
    assert summary["path"].count("validate") == 2
    assert summary["path"][-1] == "present"
    assert summary["approved"] is False
    assert summary["issues"] == ["too shallow"]


def test_complex_route_plans_before_answering(recording_llm) -> None:
    models = make_models(recording_llm, [HIGH], ['{"tier": "complex"}'])
    summary = summarize(build_graph(models).invoke({"question": LONG_QUESTION}))
    assert summary["path"] == ["classify", "plan_complex", "answer_complex", "validate", "present"]
    outline = models.answers["complex"].calls[0][-1]
    assert outline[1].startswith("Outline to follow:")
    assert summary["tokens"] == 30
    assert summary["cost"] > 0


def test_invalid_classifier_output_falls_back_to_hint(recording_llm) -> None:
    models = make_models(recording_llm, [HIGH], ["not json"])
    summary = summarize(build_graph(models).invoke({"question": LONG_QUESTION}))
    assert summary["initial_tier"] == "complex"


def test_fake_backend_runs_end_to_end(fake_settings) -> None:
    app = build_graph(build_models(fake_settings))
    summary = summarize(
        app.invoke({"question": "Compare duplicacao e complexidade cognitiva no time"})
    )
    assert summary["initial_tier"] == "medium"
    assert summary["approved"] is True
    assert summary["models"] == ["fake-classifier", "fake-medium", "fake-judge"]
    assert summary["tokens"] > 0
