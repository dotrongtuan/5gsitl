from pathlib import Path

from tools.run_testcase import execute_testcase


def test_run_testcase_dry_run(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    monkeypatch.setenv("SITL_DRY_RUN", "1")
    report = execute_testcase("testcases/latency/baseline_rtt.yaml")
    assert report.exists()
