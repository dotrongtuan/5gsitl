from tools.validate_nr_profile import validate as validate_nr
from tools.validate_slice_config import validate as validate_slice


def test_validate_nr_profile() -> None:
    data = validate_nr("configs/nr_profiles/default_mu1_30k.yaml")
    assert data["mu"] == 1
    assert data["scs_khz"] == 30


def test_validate_slice_profile() -> None:
    data = validate_slice("configs/slicing/urllc.yaml")
    assert data["name"] == "urllc"
    assert data["sst"] == 1
