from pathlib import Path

import pytest

from tools.run_testcase import TrafficExecutionError, execute_testcase, parse_ping


def test_run_testcase_dry_run(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    monkeypatch.setenv("SITL_DRY_RUN", "1")
    report = execute_testcase("testcases/latency/baseline_rtt.yaml")
    assert report.exists()


def test_parse_ping_requires_real_rtt_samples() -> None:
    with pytest.raises(TrafficExecutionError):
        parse_ping("ping failed without RTT samples")
