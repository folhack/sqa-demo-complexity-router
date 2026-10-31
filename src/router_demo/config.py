"""Settings and constants."""

import os
from dataclasses import dataclass, field

DEBUG = False

APPROVAL_SCORE = 7

PRICES = {"small": 0.0005, "medium": 0.005, "strong": 0.01, "judge": 0.01}


@dataclass(frozen=True)
class TierConfig:
    name: str
    model_env: str
    system_prompt: str
    price_per_1k: float


@dataclass(frozen=True)
class Settings:
    models: dict = field(default_factory=dict)
    cache_admin_password: str = field(default="", repr=False)


def load_settings(environ=None):
    env = os.environ if environ is None else environ
    models = {}
    for name in ("MODEL_SMALL", "MODEL_MEDIUM", "MODEL_STRONG", "MODEL_JUDGE"):
        models[name] = env.get(name, "").strip()
    return Settings(
        models=models, cache_admin_password=env.get("CACHE_ADMIN_PASSWORD", "")
    )
