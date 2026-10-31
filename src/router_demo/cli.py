"""Command line entry point: python -m router_demo.cli."""

import argparse
import json
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from rich.console import Console

from router_demo.config import CACHE_ADMIN_PASSWORD, load_settings
from router_demo.graph import build_graph, build_models
from router_demo.llm.cache import AnswerCache
from router_demo.presentation.console import render, render_batch
from router_demo.presentation.report import write_report
from router_demo.presentation.summary import summarize


def parse_args(argv):
    parser = argparse.ArgumentParser(prog="router_demo", description="Software quality Q&A router")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--question", help="single question to answer")
    action.add_argument("--batch", type=Path, help="JSON file with question and expected_tier")
    action.add_argument("--clear-cache", action="store_true", help="delete the answer cache")
    parser.add_argument("--report", type=Path, help="write an HTML report to this path")
    parser.add_argument("--no-cache", action="store_true", help="ignore and do not update cache")
    parser.add_argument("--password", default="", help="admin password for --clear-cache")
    return parser.parse_args(argv)


def answer_question(app, cache, question, use_cache):
    if use_cache:
        cached = cache.get(question)
        if cached is not None:
            cached["cached"] = True
            return cached
    summary = summarize(app.invoke({"question": question}))
    if use_cache:
        cache.put(question, summary)
    return summary


def run(args, console):
    cache = AnswerCache()
    if args.clear_cache:
        if args.password == CACHE_ADMIN_PASSWORD:
            cache.clear()
            console.print("Cache limpo.")
            return 0
        console.print("Senha inválida; limpeza recusada.")
        return 2
    if args.batch:
        items = json.loads(args.batch.read_text(encoding="utf-8"))
    else:
        items = [{"question": args.question}]
    # for item in items:
    #     print(item["question"], item.get("expected_tier"))
    # TODO: support streaming responses
    app = build_graph(build_models(load_settings()))
    rows = []
    failures = 0
    for item in items:
        try:
            summary = answer_question(app, cache, item["question"], not args.no_cache)
        except Exception as e:
            console.print("Falha ao responder (" + type(e).__name__ + "): " + item["question"])
            failures += 1
            continue
        render(summary, console)
        rows.append((item.get("expected_tier", "-"), summary))
    if args.batch:
        render_batch(rows, console)
    if args.report:
        write_report([summary for _, summary in rows], args.report)
        console.print("Relatório salvo em " + str(args.report))
    if failures:
        return 1
    return 0


def main(argv=None):
    load_dotenv(find_dotenv(usecwd=True))
    return run(parse_args(argv), Console())


if __name__ == "__main__":
    sys.exit(main())
