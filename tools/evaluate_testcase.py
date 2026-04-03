from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.common import load_json

KPI_RULES: dict[str, tuple[str, str, str]] = {
    "max_avg_rtt_ms": ("avg_rtt_ms", "max", "rtt"),
    "max_p95_rtt_ms": ("p95_rtt_ms", "max", "rtt"),
    "max_p99_rtt_ms": ("p99_rtt_ms", "max", "rtt"),
    "max_loss_pct": ("packet_loss_pct", "max", "loss"),
    "max_packet_loss_pct": ("packet_loss_pct", "max", "loss"),
    "max_jitter_ms": ("jitter_ms", "max", "jitter"),
    "min_throughput_mbps": ("throughput_mbps", "min", "throughput"),
}


def _capability_enabled(observations: dict[str, Any], capability: str) -> bool:
    caps = observations.get("metric_capabilities", {})
    return bool(caps.get(capability, False))


def evaluate_payload(testcase: dict[str, Any], metrics: dict[str, Any], observations: dict[str, Any] | None = None) -> dict[str, Any]:
    observations = observations or {}
    expected = dict(testcase.get("expected_kpis", {}))

    passed_checks: list[dict[str, Any]] = []
    failed_checks: list[dict[str, Any]] = []
    unevaluated_checks: list[dict[str, Any]] = []

    for key, expected_value in expected.items():
        if key == "attach_success":
            actual = bool(observations.get("attach_success", False))
            detail = {"name": key, "expected": bool(expected_value), "actual": actual}
            if actual == bool(expected_value):
                passed_checks.append(detail)
            else:
                failed_checks.append(detail)
            continue

        if key == "ue_ip_allocated":
            actual = bool(observations.get("ue_ip"))
            detail = {
                "name": key,
                "expected": bool(expected_value),
                "actual": actual,
                "ue_ip": observations.get("ue_ip", ""),
            }
            if actual == bool(expected_value):
                passed_checks.append(detail)
            else:
                failed_checks.append(detail)
            continue

        if key not in KPI_RULES:
            unevaluated_checks.append(
                {"name": key, "expected": expected_value, "reason": "unsupported_kpi"}
            )
            continue

        metric_name, direction, capability = KPI_RULES[key]
        actual = metrics.get(metric_name)
        if not _capability_enabled(observations, capability) or actual is None:
            unevaluated_checks.append(
                {
                    "name": key,
                    "expected": expected_value,
                    "metric": metric_name,
                    "reason": "metric_unavailable",
                }
            )
            continue

        actual_value = float(actual)
        expected_numeric = float(expected_value)
        ok = actual_value <= expected_numeric if direction == "max" else actual_value >= expected_numeric
        detail = {
            "name": key,
            "metric": metric_name,
            "expected": expected_numeric,
            "actual": actual_value,
            "operator": "<=" if direction == "max" else ">=",
        }
        if ok:
            passed_checks.append(detail)
        else:
            failed_checks.append(detail)

    if failed_checks:
        status = "FAIL"
    elif unevaluated_checks:
        status = "INCOMPLETE"
    else:
        status = "PASS"

    return {
        "status": status,
        "passed": len(passed_checks),
        "failed": len(failed_checks),
        "unevaluated": len(unevaluated_checks),
        "synthetic": bool(observations.get("synthetic", False)),
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "unevaluated_checks": unevaluated_checks,
    }


def evaluate_report(path: str | Path) -> dict[str, Any]:
    report = load_json(path, {})
    testcase = dict(report.get("testcase", {}))
    metrics = dict(report.get("metrics", {}))
    observations = dict(report.get("observations", {}))
    return evaluate_payload(testcase, metrics, observations)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report_path")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()

    evaluation = evaluate_report(args.report_path)
    if args.summary_only:
        print(evaluation["status"])
    else:
        print(json.dumps(evaluation, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
