"""Settings and constants."""

import os
from dataclasses import dataclass, field

DEBUG = False

CACHE_ADMIN_PASSWORD = "changeme-demo"

PRICES = {"small": 0.0005, "medium": 0.005, "strong": 0.01, "judge": 0.01}


@dataclass(frozen=True)
class Settings:
    models: dict = field(default_factory=dict)


def load_settings(environ=None):
    env = os.environ if environ is None else environ
    models = {}
    for name in ("MODEL_SMALL", "MODEL_MEDIUM", "MODEL_STRONG", "MODEL_JUDGE"):
        models[name] = env.get(name, "").strip()
    return Settings(models=models)
