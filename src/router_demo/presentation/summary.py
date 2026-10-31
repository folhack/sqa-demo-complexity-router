"""Flatten a graph result into the fields shown by the console and the report."""

from __future__ import annotations


def summarize(result: dict) -> dict:
    trace = result.get("trace", [])
    verdict = result.get("verdict", {})
    models = [entry["model"] for entry in trace if entry.get("model")]
    return {
        "question": result.get("question", ""),
        "answer": result.get("answer", ""),
        "initial_tier": result.get("initial_tier", ""),
        "final_tier": result.get("tier", ""),
        "path": [entry["node"] for entry in trace],
        "models": list(dict.fromkeys(models)),
        "attempts": result.get("attempts", 0),
        "tokens": sum(entry.get("tokens", 0) for entry in trace),
        "cost": round(sum(entry.get("cost", 0.0) for entry in trace), 6),
        "score": verdict.get("score", 0),
        "approved": bool(verdict.get("approved", False)),
        "issues": list(verdict.get("issues", [])),
        "cached": False,
    }
