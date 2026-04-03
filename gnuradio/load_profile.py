from __future__ import annotations

from pathlib import Path

import yaml


def load_profile(path: str) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
