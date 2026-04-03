from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Any

import yaml

try:
    import fcntl
except ImportError:
    fcntl = None
    import msvcrt

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


def _atomic_write(path: str | Path, writer: Callable[[TextIOWrapper], None]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{out.name}.", suffix=".tmp", dir=out.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            writer(handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, out)
    finally:
        if tmp.exists():
            tmp.unlink()
    return out


def dump_json(path: str | Path, payload: Any) -> Path:
    return _atomic_write(path, lambda handle: json.dump(payload, handle, indent=2, sort_keys=True))


def dump_text(path: str | Path, content: str) -> Path:
    return _atomic_write(path, lambda handle: handle.write(content))


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


def runtime_state_paths() -> tuple[Path, Path]:
    return (
        env_path("STATE_FILE", "outputs/runtime/state.json"),
        env_path("STATE_ENV_FILE", "outputs/runtime/omnetpp.env"),
    )


def runtime_state_lock_path(state_file: Path | None = None) -> Path:
    resolved_state_file = state_file or runtime_state_paths()[0]
    fallback = resolved_state_file.with_name(f"{resolved_state_file.name}.lock")
    return Path(os.environ.get("STATE_LOCK_FILE", str(fallback)))


def _acquire_lock(handle: Any) -> None:
    if fcntl is not None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        return
    handle.seek(0, os.SEEK_END)
    if handle.tell() == 0:
        handle.write(b"\0")
        handle.flush()
    handle.seek(0)
    msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)


def _release_lock(handle: Any) -> None:
    if fcntl is not None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return
    handle.seek(0)
    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


@contextmanager
def file_lock(path: str | Path) -> Iterator[None]:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a+b") as handle:
        _acquire_lock(handle)
        try:
            yield
        finally:
            _release_lock(handle)


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
    path = runtime_state_paths()[0]
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


def _save_runtime_state_locked(state: dict[str, Any], state_file: Path, env_file: Path) -> Path:
    state["updated_at"] = now_iso()
    dump_json(state_file, state)
    dump_text(env_file, flatten_state(state))
    return state_file


def mutate_runtime_state(mutator: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    state_file, env_file = runtime_state_paths()
    with file_lock(runtime_state_lock_path(state_file)):
        state = load_json(state_file, default_runtime_state())
        mutator(state)
        _save_runtime_state_locked(state, state_file, env_file)
        return state


def save_runtime_state(state: dict[str, Any]) -> Path:
    state_file, env_file = runtime_state_paths()
    with file_lock(runtime_state_lock_path(state_file)):
        return _save_runtime_state_locked(state, state_file, env_file)


def update_runtime_state(*, component: str | None = None, state_value: str | None = None, **fields: Any) -> dict[str, Any]:
    def apply(state: dict[str, Any]) -> None:
        if component:
            if component == "all":
                for key in state["components"]:
                    state["components"][key] = state_value or state["components"][key]
            else:
                state["components"][component] = state_value or state["components"].get(component, "unknown")
        for key, value in fields.items():
            if value is not None:
                state[key] = value

    return mutate_runtime_state(apply)


def record_event(kind: str, message: str, **payload: Any) -> None:
    entry = {"ts": now_iso(), "kind": kind, "message": message, "payload": payload}
    event_log = env_path("EVENT_LOG", "outputs/runtime/events.jsonl")

    def apply(state: dict[str, Any]) -> None:
        append_jsonl(event_log, entry)
        recent = state.get("recent_events", [])
        recent.append(entry)
        state["recent_events"] = recent[-20:]

    mutate_runtime_state(apply)


def set_component_state(component: str, state_value: str) -> dict[str, Any]:
    entry = {
        "ts": now_iso(),
        "kind": "component.state",
        "message": f"{component} -> {state_value}",
        "payload": {"component": component, "state": state_value},
    }
    event_log = env_path("EVENT_LOG", "outputs/runtime/events.jsonl")

    def apply(state: dict[str, Any]) -> None:
        if component == "all":
            for key in state["components"]:
                state["components"][key] = state_value or state["components"][key]
        else:
            state["components"][component] = state_value or state["components"].get(component, "unknown")
        append_jsonl(event_log, entry)
        recent = state.get("recent_events", [])
        recent.append(entry)
        state["recent_events"] = recent[-20:]

    return mutate_runtime_state(apply)
