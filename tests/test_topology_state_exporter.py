from tools.common import load_runtime_state, save_runtime_state, update_runtime_state


def test_runtime_state_roundtrip(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "state.json"))
    monkeypatch.setenv("STATE_ENV_FILE", str(tmp_path / "omnetpp.env"))
    save_runtime_state(load_runtime_state())
    update_runtime_state(component="core", state_value="up", active_testcase="demo")
    state = load_runtime_state()
    assert state["components"]["core"] == "up"
    assert state["active_testcase"] == "demo"
