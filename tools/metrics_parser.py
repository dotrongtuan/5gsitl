from __future__ import annotations

import argparse
import csv

from tools.common import load_json, outputs_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("metrics_path")
    args = parser.parse_args()

    metrics = load_json(args.metrics_path, {})
    out = outputs_dir("csv") / "latency_latest.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["current_rtt_ms", "avg_rtt_ms", "p95_rtt_ms", "p99_rtt_ms", "throughput_mbps", "packet_loss_pct", "jitter_ms"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "current_rtt_ms": metrics.get("current_rtt_ms", 0.0),
                "avg_rtt_ms": metrics.get("avg_rtt_ms", 0.0),
                "p95_rtt_ms": metrics.get("p95_rtt_ms", 0.0),
                "p99_rtt_ms": metrics.get("p99_rtt_ms", 0.0),
                "throughput_mbps": metrics.get("throughput_mbps", 0.0),
                "packet_loss_pct": metrics.get("packet_loss_pct", 0.0),
                "jitter_ms": metrics.get("jitter_ms", 0.0),
            }
        )
    print(out)


if __name__ == "__main__":
    main()
