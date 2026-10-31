"""HTML report rendered with Jinja2."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"


def render_report(summaries):
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=False)
    return env.get_template("report.html").render(results=summaries)


def write_report(summaries, path):
    path.write_text(render_report(summaries), encoding="utf-8")
