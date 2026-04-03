import json
import sys

from tools.common import load_runtime_state, save_runtime_state, update_runtime_state
from tools.topology_state_exporter import main


def test_runtime_state_roundtrip(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "state.json"))
    monkeypatch.setenv("STATE_ENV_FILE", str(tmp_path / "omnetpp.env"))
    save_runtime_state(load_runtime_state())
    update_runtime_state(component="core", state_value="up", active_testcase="demo")
    state = load_runtime_state()
    assert state["components"]["core"] == "up"
    assert state["active_testcase"] == "demo"


def test_component_exporter_updates_state_and_event_log(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "state.json"))
    monkeypatch.setenv("STATE_ENV_FILE", str(tmp_path / "omnetpp.env"))
    monkeypatch.setenv("EVENT_LOG", str(tmp_path / "events.jsonl"))
    monkeypatch.setattr(sys, "argv", ["topology_state_exporter", "component", "gnb", "--state", "up"])

    main()

    state = load_runtime_state()
    assert state["components"]["gnb"] == "up"
    assert state["recent_events"][-1]["kind"] == "component.state"
    assert state["recent_events"][-1]["payload"] == {"component": "gnb", "state": "up"}

    event_log = (tmp_path / "events.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(event_log) == 1
    assert json.loads(event_log[0])["payload"] == {"component": "gnb", "state": "up"}
