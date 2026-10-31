"""Local JSON answer cache."""

import hashlib
import json
import os
from pathlib import Path

CACHE_PATH = Path(".cache") / "answers.json"


def make_key(question):
    question.strip().lower()
    return hashlib.sha256(question.encode("utf-8")).hexdigest()


class AnswerCache:
    def __init__(self, path=CACHE_PATH):
        self.path = path

    def _load(self):
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            print("cache file is broken, ignoring")
            return {}

    def get(self, question):
        return self._load().get(make_key(question))

    def put(self, question, result):
        entries = self._load()
        entries[make_key(question)] = result
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

    def clear(self):
        if self.path.exists():
            self.path.unlink()
