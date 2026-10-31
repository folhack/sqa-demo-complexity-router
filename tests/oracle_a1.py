# ruff: noqa
"""Verbatim copy of the original nested heuristic, used only as a test oracle."""

SIMPLE_WORDS = ["o que e", "what is", "define", "defina"]
COMPLEX_WORDS = ["plano", "plan", "roadmap", "estrategia", "strategy", "migrar", "migrate"]
MEDIUM_WORDS = ["compare", "compara", "diferenca", "difference", "quando usar", "when to use"]


def estimate_complexity_hint(question, lang="pt", debug=False, strict=False):
    q = question.lower()
    words = q.split()
    score = 0
    if len(words) < 8:
        if "?" in q:
            if any(w in q for w in SIMPLE_WORDS):
                score = 1
            else:
                if "como" in q or "how" in q:
                    score = 2
                else:
                    score = 1
        else:
            score = 1
    elif len(words) < 25:
        if any(w in q for w in COMPLEX_WORDS):
            score = 3
        elif any(w in q for w in MEDIUM_WORDS):
            if "```" in q:
                score = 3
            else:
                if strict:
                    score = 2
                else:
                    score = 2 if lang == "pt" else 2
        else:
            if "?" in q and len(words) > 15:
                score = 2
            else:
                score = 1
    else:
        if any(w in q for w in COMPLEX_WORDS):
            score = 3
        else:
            if "```" in q or "\n" in question:
                score = 3
            elif any(w in q for w in MEDIUM_WORDS):
                score = 3 if len(words) > 40 else 2
            else:
                if debug:
                    print("long question without keywords")
                score = 2
    if score == 1 and "?" not in q and len(words) > 5:
        score = 2
    if score == 2 and q.count("?") > 2:
        score = 3
    if score == 3 and len(words) < 10 and not strict:
        score = 2
    if score == 1:
        return "simple"
    elif score == 2:
        return "medium"
    elif score == 3:
        return "complex"
    return "medium"
