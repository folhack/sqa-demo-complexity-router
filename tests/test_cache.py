from __future__ import annotations

import hashlib
import re

from router_demo.llm.cache import AnswerCache, make_key


def test_key_is_normalized() -> None:
    assert make_key("  A ") == make_key("a")
    assert make_key("What is X?") == make_key("what is x?  ")


def test_key_is_sha256_of_normalized_question() -> None:
    key = make_key("  Bus Factor ")
    assert re.fullmatch(r"[0-9a-f]{64}", key)
    assert key == hashlib.sha256(b"bus factor").hexdigest()


def test_cache_round_trip_and_clear(tmp_path) -> None:
    cache = AnswerCache(tmp_path / ".cache" / "answers.json")
    assert cache.get("q") is None
    cache.put("Q ", {"answer": "x"})
    assert cache.get(" q") == {"answer": "x"}
    cache.clear()
    assert cache.get("q") is None
    cache.clear()
