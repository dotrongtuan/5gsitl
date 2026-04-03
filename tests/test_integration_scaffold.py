import pytest

from tools.common import load_runtime_state, update_runtime_state


@pytest.mark.integration
def test_core_up_contract() -> None:
    update_runtime_state(component="core", state_value="up")
    assert load_runtime_state()["components"]["core"] == "up"


@pytest.mark.integration
def test_gnb_start_contract() -> None:
    update_runtime_state(component="gnb", state_value="up")
    assert load_runtime_state()["components"]["gnb"] == "up"


@pytest.mark.integration
def test_ue_attach_contract() -> None:
    update_runtime_state(component="ue", state_value="up", attach_state="attached", ue_ip="10.45.0.2")
    state = load_runtime_state()
    assert state["attach_state"] == "attached"
    assert state["ue_ip"] == "10.45.0.2"


@pytest.mark.integration
def test_traffic_and_capture_contract() -> None:
    update_runtime_state(component="capture", state_value="active")
    assert load_runtime_state()["components"]["capture"] == "active"


@pytest.mark.integration
def test_omnetpp_state_export_contract() -> None:
    update_runtime_state(component="omnetpp", state_value="up")
    assert load_runtime_state()["components"]["omnetpp"] == "up"
