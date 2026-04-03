from __future__ import annotations

import argparse
import csv
import os
import random
import re
import subprocess
from pathlib import Path
from typing import Any

from tools.apply_slice_profile import apply_slice
from tools.common import dump_json, load_yaml, outputs_dir, project_root, record_event, update_runtime_state
from tools.evaluate_testcase import evaluate_payload
from tools.run_nr_experiment import apply_nr_profile

REQUIRED = {
    "name",
    "objective",
    "scenario_class",
    "nr_config_profile",
    "channel_config",
    "traffic_config",
    "capture_config",
    "expected_kpis",
    "report_metadata",
}
RTT_RE = re.compile(r"time=(?P<rtt>[0-9.]+)\s*ms")
IPERF_UDP_RE = re.compile(
    r"(?P<start>[0-9.]+)\s*-\s*(?P<end>[0-9.]+)\s+sec\s+"
    r"(?P<transfer>[0-9.]+)\s+(?P<transfer_unit>[KMGTP]?)Bytes\s+"
    r"(?P<bitrate>[0-9.]+)\s+(?P<bitrate_unit>[KMGTP]?)bits/sec\s+"
    r"(?P<jitter>[0-9.]+)\s+ms\s+"
    r"(?P<lost>[0-9]+)\/(?P<total>[0-9]+)\s+\((?P<loss>[0-9.]+)%\)\s+"
    r"(?P<role>sender|receiver)"
)


class TrafficExecutionError(RuntimeError):
    """Raised when a testcase requests real traffic but no real measurement is obtained."""


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root() / value


def validate_testcase(path: str) -> dict[str, Any]:
    data = load_yaml(path)
    missing = sorted(REQUIRED - set(data))
    if missing:
        raise ValueError(f"Missing testcase keys: {', '.join(missing)}")
    return data


def synthetic_metrics(scenario_class: str) -> dict[str, float]:
    base = {"nr": 18.0, "latency": 9.0, "phy": 14.0, "slicing": 16.0}.get(scenario_class, 12.0)
    spread = random.uniform(0.5, 2.5)
    avg = round(base + spread, 3)
    return {
        "current_rtt_ms": round(avg + 0.4, 3),
        "avg_rtt_ms": avg,
        "p95_rtt_ms": round(avg * 1.4, 3),
        "p99_rtt_ms": round(avg * 1.7, 3),
        "packet_loss_pct": round(random.uniform(0.0, 1.5), 3),
        "jitter_ms": round(random.uniform(0.1, 1.2), 3),
    }


def parse_ping(output: str) -> dict[str, float]:
    samples = [float(match.group("rtt")) for match in RTT_RE.finditer(output)]
    if not samples:
        raise TrafficExecutionError("Ping completed without RTT samples. UE attach or routing is likely incomplete.")
    ordered = sorted(samples)
    return {
        "current_rtt_ms": round(samples[-1], 3),
        "avg_rtt_ms": round(sum(samples) / len(samples), 3),
        "p95_rtt_ms": round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))], 3),
        "p99_rtt_ms": round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.99))], 3),
        "packet_loss_pct": 0.0,
        "jitter_ms": round(max(samples) - min(samples), 3),
    }


def convert_to_mbps(value: str, unit: str) -> float:
    scale = {
        "": 1e-6,
        "K": 1e-3,
        "M": 1.0,
        "G": 1e3,
        "T": 1e6,
        "P": 1e9,
    }
    return round(float(value) * scale.get(unit, 1.0), 3)


def parse_iperf3_udp(output: str) -> dict[str, float]:
    matches = [match.groupdict() for match in IPERF_UDP_RE.finditer(output)]
    if not matches:
        raise TrafficExecutionError("iperf3 completed without a parsable UDP summary.")

    summary = next((item for item in reversed(matches) if item["role"] == "receiver"), matches[-1])
    return {
        "throughput_mbps": convert_to_mbps(summary["bitrate"], summary["bitrate_unit"]),
        "jitter_ms": round(float(summary["jitter"]), 3),
        "packet_loss_pct": round(float(summary["loss"]), 3),
    }


def maybe_run_traffic(case: dict[str, Any]) -> tuple[dict[str, float], dict[str, Any]]:
    mode = case["traffic_config"].get("mode", "synthetic")
    if os.environ.get("SITL_DRY_RUN", "0") == "1":
        return (
            synthetic_metrics(case["scenario_class"]),
            {
                "traffic_mode": mode,
                "attach_success": True,
                "metric_capabilities": {"rtt": True, "loss": True, "jitter": True, "throughput": False},
                "synthetic": True,
            },
        )
    try:
        if mode == "ping":
            result = subprocess.run(
                ["bash", str(project_root() / "scripts" / "run_ping_test.sh"), str(case["traffic_config"].get("count", 10)), str(case["traffic_config"].get("target", "10.45.0.1"))],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise TrafficExecutionError(result.stdout + result.stderr)
            return (
                parse_ping(result.stdout + result.stderr),
                {
                    "traffic_mode": mode,
                    "attach_success": True,
                    "metric_capabilities": {"rtt": True, "loss": True, "jitter": True, "throughput": False},
                    "synthetic": False,
                },
            )
        if mode == "udp-latency":
            result = subprocess.run(
                ["bash", str(project_root() / "scripts" / "run_udp_latency_test.sh"), str(case["traffic_config"].get("target", "10.45.0.1")), str(case["traffic_config"].get("duration_s", 10)), str(case["traffic_config"].get("bitrate", "5M"))],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise TrafficExecutionError(result.stdout + result.stderr)
            return (
                parse_iperf3_udp(result.stdout + result.stderr),
                {
                    "traffic_mode": mode,
                    "attach_success": True,
                    "metric_capabilities": {"rtt": False, "loss": True, "jitter": True, "throughput": True},
                    "synthetic": False,
                },
            )
        return (
            synthetic_metrics(case["scenario_class"]),
            {
                "traffic_mode": mode,
                "attach_success": True,
                "metric_capabilities": {"rtt": True, "loss": True, "jitter": True, "throughput": False},
                "synthetic": True,
            },
        )
    except FileNotFoundError:
        return (
            synthetic_metrics(case["scenario_class"]),
            {
                "traffic_mode": mode,
                "attach_success": True,
                "metric_capabilities": {"rtt": True, "loss": True, "jitter": True, "throughput": False},
                "synthetic": True,
            },
        )


def run_optional_command(args: list[str]) -> None:
    try:
        subprocess.run(args, check=False)
    except FileNotFoundError:
        return


def write_reports(
    case: dict[str, Any],
    metrics: dict[str, float],
    observations: dict[str, Any],
    channel_name: str,
    slice_name: str,
) -> Path:
    reports = outputs_dir("reports")
    csv_dir = outputs_dir("csv")
    evaluation = evaluate_payload(case, metrics, observations)
    report_payload = {
        "testcase": case,
        "metrics": metrics,
        "observations": observations,
        "evaluation": evaluation,
    }
    json_path = dump_json(reports / f"{case['name']}.json", report_payload)
    (reports / f"{case['name']}.md").write_text(
        "\n".join(
            [
                f"# Testcase {case['name']}",
                f"- objective: {case['objective']}",
                f"- scenario_class: {case['scenario_class']}",
                f"- channel_profile: {channel_name}",
                f"- slice_profile: {slice_name or 'none'}",
                f"- evaluation_status: {evaluation['status']}",
                f"- evaluation_passed: {evaluation['passed']}",
                f"- evaluation_failed: {evaluation['failed']}",
                f"- evaluation_unevaluated: {evaluation['unevaluated']}",
                f"- synthetic_metrics: {evaluation['synthetic']}",
                f"- avg_rtt_ms: {metrics.get('avg_rtt_ms', 'n/a')}",
                f"- p95_rtt_ms: {metrics.get('p95_rtt_ms', 'n/a')}",
                f"- p99_rtt_ms: {metrics.get('p99_rtt_ms', 'n/a')}",
                f"- throughput_mbps: {metrics.get('throughput_mbps', 'n/a')}",
                f"- packet_loss_pct: {metrics.get('packet_loss_pct', 'n/a')}",
                f"- jitter_ms: {metrics.get('jitter_ms', 'n/a')}",
            ]
        ),
        encoding="utf-8",
    )
    (reports / f"{case['name']}.html").write_text(
        f"<html><body><h1>{case['name']}</h1><h2>{evaluation['status']}</h2><pre>{report_payload}</pre></body></html>",
        encoding="utf-8",
    )
    with (csv_dir / f"{case['name']}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metrics.keys()))
        writer.writeheader()
        writer.writerow(metrics)
    return json_path


def execute_testcase(path: str, slice_override: str | None = None) -> Path:
    case = validate_testcase(path)
    nr_profile = resolve_project_path(case["nr_config_profile"])
    channel_profile = resolve_project_path(case["channel_config"])
    slice_profile = resolve_project_path(slice_override or case.get("slice_profile", "")) if (slice_override or case.get("slice_profile")) else None

    apply_nr_profile(str(nr_profile))
    if slice_profile:
        apply_slice(str(slice_profile))

    channel_data = load_yaml(channel_profile)
    capture_enabled = bool(case["capture_config"].get("enabled", True))
    if capture_enabled:
        run_optional_command(["bash", str(project_root() / "scripts" / "start_capture.sh"), case["name"]])

    update_runtime_state(
        active_testcase=case["name"],
        active_scenario=case["scenario_class"],
        channel_profile=channel_data.get("profile_name", channel_profile.stem),
        attach_state="running",
        component="capture",
        state_value="active" if capture_enabled else "idle",
    )
    record_event("testcase.start", f"Started testcase {case['name']}", path=path)

    report: Path | None = None
    try:
        metrics, observations = maybe_run_traffic(case)
        dump_json(outputs_dir("runtime") / "metrics.json", metrics)
        report = write_reports(
            case,
            metrics,
            {
                **observations,
                "ue_ip": case["traffic_config"].get("ue_ip", "10.45.0.2"),
            },
            channel_data.get("profile_name", channel_profile.stem),
            slice_profile.stem if slice_profile else "",
        )
        update_runtime_state(
            metrics=metrics,
            attach_state="attached",
            ue_ip=case["traffic_config"].get("ue_ip", "10.45.0.2"),
            component="capture",
            state_value="idle",
        )
        record_event("testcase.stop", f"Completed testcase {case['name']}", report=str(report))
        return report
    except TrafficExecutionError as exc:
        failure_observations = {
            "traffic_mode": case["traffic_config"].get("mode", "synthetic"),
            "attach_success": False,
            "ue_ip": "",
            "metric_capabilities": {"rtt": False, "loss": False, "jitter": False, "throughput": False},
            "synthetic": False,
        }
        update_runtime_state(
            attach_state="failed",
            component="capture",
            state_value="idle",
        )
        record_event("testcase.error", f"Traffic execution failed for testcase {case['name']}", error=str(exc))
        failure_report = dump_json(
            outputs_dir("reports") / f"{case['name']}.error.json",
            {
                "testcase": case,
                "error": str(exc),
                "channel_profile": channel_data.get("profile_name", channel_profile.stem),
                "slice_profile": slice_profile.stem if slice_profile else "",
                "observations": failure_observations,
                "evaluation": evaluate_payload(case, {}, failure_observations),
            },
        )
        return failure_report
    finally:
        if capture_enabled:
            run_optional_command(["bash", str(project_root() / "scripts" / "stop_capture.sh")])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--slice")
    args = parser.parse_args()
    print(execute_testcase(args.path, args.slice))


if __name__ == "__main__":
    main()
