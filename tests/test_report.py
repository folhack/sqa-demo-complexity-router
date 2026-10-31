from __future__ import annotations

from router_demo.presentation.report import render_report, write_report
from router_demo.presentation.summary import summarize

MALICIOUS = "<script>alert('x')</script>"


def malicious_summary() -> dict:
    return summarize(
        {
            "question": f"q {MALICIOUS}",
            "answer": MALICIOUS,
            "verdict": {"score": 3, "approved": False, "issues": [MALICIOUS]},
            "trace": [{"node": "classify", "model": "m", "tokens": 1, "cost": 0.1}],
        }
    )


def test_report_escapes_answer_question_and_issues() -> None:
    html = render_report([malicious_summary()])
    assert "<script>" not in html
    assert html.count("&lt;script&gt;") == 3
    assert "NÃO VALIDADA" in html
    assert 'lang="pt-BR"' in html


def test_write_report_creates_file(tmp_path) -> None:
    path = tmp_path / "relatorio.html"
    write_report([malicious_summary()], path)
    assert "&lt;script&gt;" in path.read_text(encoding="utf-8")
