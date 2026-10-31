"""Command line entry point: python -m router_demo.cli."""

from __future__ import annotations

import argparse
import hmac
import json
import sys
from pathlib import Path
from typing import Any

from dotenv import find_dotenv, load_dotenv
from rich.console import Console

from router_demo.config import Settings, load_settings
from router_demo.graph import build_graph, build_models
from router_demo.llm.cache import AnswerCache
from router_demo.llm.factory import LLM_ERRORS
from router_demo.presentation.console import render, render_batch
from router_demo.presentation.report import write_report
from router_demo.presentation.summary import summarize


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="router_demo", description="Software quality Q&A router")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--question", help="single question to answer")
    action.add_argument("--batch", type=Path, help="JSON file with question and expected_tier")
    action.add_argument("--clear-cache", action="store_true", help="delete the answer cache")
    parser.add_argument("--report", type=Path, help="write an HTML report to this path")
    parser.add_argument("--no-cache", action="store_true", help="ignore and do not update cache")
    parser.add_argument("--password", default="", help="admin password for --clear-cache")
    return parser.parse_args(argv)


def load_batch(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def answer_question(app: Any, cache: AnswerCache, question: str, use_cache: bool) -> dict:
    cached = cache.get(question) if use_cache else None
    if cached is not None:
        return {**cached, "cached": True}
    summary = summarize(app.invoke({"question": question}))
    if use_cache:
        cache.put(question, summary)
    return summary


def clear_cache(settings: Settings, password: str, cache: AnswerCache, console: Console) -> int:
    expected = settings.cache_admin_password
    if not expected:
        console.print("CACHE_ADMIN_PASSWORD não definida; limpeza recusada.")
        return 2
    if not hmac.compare_digest(password.encode("utf-8"), expected.encode("utf-8")):
        console.print("Senha inválida; limpeza recusada.")
        return 2
    cache.clear()
    console.print("Cache limpo.")
    return 0


def run(args: argparse.Namespace, settings: Settings, console: Console) -> int:
    cache = AnswerCache()
    if args.clear_cache:
        return clear_cache(settings, args.password, cache, console)
    items = load_batch(args.batch) if args.batch else [{"question": args.question}]
    app = build_graph(build_models(settings))
    rows, failures = [], 0
    for item in items:
        try:
            summary = answer_question(app, cache, item["question"], not args.no_cache)
        except LLM_ERRORS as exc:
            console.print(f"Falha ao responder ({type(exc).__name__}): {item['question']}")
            failures += 1
            continue
        render(summary, console)
        rows.append((item.get("expected_tier", "-"), summary))
    if args.batch:
        render_batch(rows, console)
    if args.report:
        write_report([summary for _, summary in rows], args.report)
        console.print(f"Relatório salvo em {args.report}")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    load_dotenv(find_dotenv(usecwd=True))
    return run(parse_args(argv), load_settings(), Console())


if __name__ == "__main__":
    sys.exit(main())
