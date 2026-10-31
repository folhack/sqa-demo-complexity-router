"""HTML report rendered with Jinja2 (autoescape on)."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).parent / "templates"


def render_report(summaries: list[dict]) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR), autoescape=select_autoescape(["html"])
    )
    return env.get_template("report.html").render(results=summaries)


def write_report(summaries: list[dict], path: Path) -> None:
    path.write_text(render_report(summaries), encoding="utf-8")
