from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def project_root() -> Path:
    return ROOT


def runtime_dir() -> Path:
    path = ROOT / "outputs" / "runtime"
    path.mkdir(parents=True, exist_ok=True)
    return path


def outputs_dir(name: str) -> Path:
    path = ROOT / "outputs" / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping")
    return data


def dump_json(path: str | Path, payload: Any) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
    tmp.replace(out)
    return out


def load_json(path: str | Path, default: Any) -> Any:
    candidate = Path(path)
    if not candidate.exists():
        return default
    try:
        with candidate.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return default


def append_jsonl(path: str | Path, record: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def env_path(name: str, fallback: str) -> Path:
    return Path(os.environ.get(name, str(ROOT / fallback)))


def default_runtime_state() -> dict[str, Any]:
    return {
        "updated_at": now_iso(),
        "components": {
            "core": "down",
            "gnb": "down",
            "ue": "down",
            "channel": "down",
            "omnetpp": "down",
            "capture": "idle",
            "adapters": "down",
        },
        "active_testcase": "",
        "active_scenario": "",
        "active_slice": "",
        "nr_profile": "",
        "channel_profile": "",
        "attach_state": "detached",
        "ue_ip": "",
        "metrics": {
            "current_rtt_ms": 0.0,
            "avg_rtt_ms": 0.0,
            "p95_rtt_ms": 0.0,
            "p99_rtt_ms": 0.0,
            "packet_loss_pct": 0.0,
            "jitter_ms": 0.0,
        },
        "recent_events": [],
    }


def load_runtime_state() -> dict[str, Any]:
    path = env_path("STATE_FILE", "outputs/runtime/state.json")
    return load_json(path, default_runtime_state())


def flatten_state(state: dict[str, Any]) -> str:
    metrics = state.get("metrics", {})
    lines = [
        f"component.core={state['components'].get('core', 'down')}",
        f"component.gnb={state['components'].get('gnb', 'down')}",
        f"component.ue={state['components'].get('ue', 'down')}",
        f"component.channel={state['components'].get('channel', 'down')}",
        f"component.omnetpp={state['components'].get('omnetpp', 'down')}",
        f"component.capture={state['components'].get('capture', 'idle')}",
        f"component.adapters={state['components'].get('adapters', 'down')}",
        f"active_testcase={state.get('active_testcase', '')}",
        f"active_scenario={state.get('active_scenario', '')}",
        f"active_slice={state.get('active_slice', '')}",
        f"nr_profile={state.get('nr_profile', '')}",
        f"channel_profile={state.get('channel_profile', '')}",
        f"attach_state={state.get('attach_state', 'detached')}",
        f"ue_ip={state.get('ue_ip', '')}",
        f"metric.current_rtt_ms={metrics.get('current_rtt_ms', 0.0)}",
        f"metric.avg_rtt_ms={metrics.get('avg_rtt_ms', 0.0)}",
        f"metric.p95_rtt_ms={metrics.get('p95_rtt_ms', 0.0)}",
        f"metric.p99_rtt_ms={metrics.get('p99_rtt_ms', 0.0)}",
        f"metric.packet_loss_pct={metrics.get('packet_loss_pct', 0.0)}",
        f"metric.jitter_ms={metrics.get('jitter_ms', 0.0)}",
    ]
    return "\n".join(lines) + "\n"


def save_runtime_state(state: dict[str, Any]) -> Path:
    state["updated_at"] = now_iso()
    state_file = env_path("STATE_FILE", "outputs/runtime/state.json")
    env_file = env_path("STATE_ENV_FILE", "outputs/runtime/omnetpp.env")
    dump_json(state_file, state)
    env_file.write_text(flatten_state(state), encoding="utf-8")
    return state_file


def update_runtime_state(*, component: str | None = None, state_value: str | None = None, **fields: Any) -> dict[str, Any]:
    state = load_runtime_state()
    if component:
        if component == "all":
            for key in state["components"]:
                state["components"][key] = state_value or state["components"][key]
        else:
            state["components"][component] = state_value or state["components"].get(component, "unknown")
    for key, value in fields.items():
        if value is not None:
            state[key] = value
    save_runtime_state(state)
    return state


def record_event(kind: str, message: str, **payload: Any) -> None:
    entry = {"ts": now_iso(), "kind": kind, "message": message, "payload": payload}
    append_jsonl(env_path("EVENT_LOG", "outputs/runtime/events.jsonl"), entry)
    state = load_runtime_state()
    recent = state.get("recent_events", [])
    recent.append(entry)
    state["recent_events"] = recent[-20:]
    save_runtime_state(state)
