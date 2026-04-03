from __future__ import annotations

from tools.common import dump_json, env_path, load_json


def snapshot_files() -> dict:
    state = load_json(env_path("STATE_FILE", "outputs/runtime/state.json"), {})
    metrics = load_json(env_path("METRICS_FILE", "outputs/runtime/metrics.json"), {})
    return {"state": state, "metrics": metrics}


def write_snapshot(path: str) -> None:
    dump_json(path, snapshot_files())
