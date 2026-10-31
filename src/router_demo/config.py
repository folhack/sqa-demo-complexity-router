"""Settings and shared constants."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

APPROVAL_SCORE = 7
MAX_ATTEMPTS = 2
SHORTCUT_MAX_WORDS = 8
MODEL_ENVS = ("MODEL_SMALL", "MODEL_MEDIUM", "MODEL_STRONG", "MODEL_JUDGE")
FAKE_BACKEND = "fake"


@dataclass(frozen=True)
class TierConfig:
    name: str
    model_env: str
    system_prompt: str
    price_per_1k: float


@dataclass(frozen=True)
class Settings:
    backend: str = "openai"
    models: Mapping[str, str] = field(default_factory=dict)
    cache_admin_password: str = field(default="", repr=False)


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if environ is None else environ
    return Settings(
        backend=env.get("LLM_BACKEND", "openai").strip().lower(),
        models={name: env.get(name, "").strip() for name in MODEL_ENVS},
        cache_admin_password=env.get("CACHE_ADMIN_PASSWORD", ""),
    )
