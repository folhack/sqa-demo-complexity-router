"""Flatten a graph result into the fields shown by the console and the report."""


def summarize(result):
    trace = result.get("trace", [])
    verdict = result.get("verdict", {})
    count = len(trace)
    models = []
    for entry in trace:
        if entry.get("model") and entry["model"] not in models:
            models.append(entry["model"])
    tokens = 0
    cost = 0.0
    for entry in trace:
        tokens += entry.get("tokens", 0)
        cost += entry.get("cost", 0.0)
    return {
        "question": result.get("question", ""),
        "answer": result.get("answer", ""),
        "initial_tier": result.get("initial_tier", ""),
        "final_tier": result.get("tier", ""),
        "path": [entry["node"] for entry in trace],
        "models": models,
        "attempts": result.get("attempts", 0),
        "tokens": tokens,
        "cost": round(cost, 6),
        "score": verdict.get("score", 0),
        "approved": bool(verdict.get("approved", False)),
        "issues": list(verdict.get("issues", [])),
        "cached": False,
    }
