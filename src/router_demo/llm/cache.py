"""Local JSON answer cache keyed by the normalized question."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

CACHE_PATH = Path(".cache") / "answers.json"


def make_key(question: str) -> str:
    normalized = question.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class AnswerCache:
    def __init__(self, path: Path = CACHE_PATH) -> None:
        self.path = path

    def _load(self) -> dict[str, dict]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def get(self, question: str) -> dict | None:
        return self._load().get(make_key(question))

    def put(self, question: str, result: dict) -> None:
        entries = self._load()
        entries[make_key(question)] = result
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)
