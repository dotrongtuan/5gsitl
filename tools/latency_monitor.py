from __future__ import annotations

import argparse
import re
from statistics import mean

from tools.common import dump_json, outputs_dir

RTT_RE = re.compile(r"time=(?P<rtt>[0-9.]+)\s*ms")


def parse_ping_log(text: str) -> dict:
    samples = [float(match.group("rtt")) for match in RTT_RE.finditer(text)]
    if not samples:
        return {"samples": 0, "avg_rtt_ms": 0.0, "p95_rtt_ms": 0.0, "p99_rtt_ms": 0.0}
    ordered = sorted(samples)
    p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    p99 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.99))]
    return {
        "samples": len(samples),
        "avg_rtt_ms": round(mean(samples), 3),
        "p95_rtt_ms": round(p95, 3),
        "p99_rtt_ms": round(p99, 3),
        "current_rtt_ms": round(samples[-1], 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("logfile")
    args = parser.parse_args()
    payload = parse_ping_log(open(args.logfile, encoding="utf-8").read())
    out = dump_json(outputs_dir("runtime") / "latency_summary.json", payload)
    print(out)


if __name__ == "__main__":
    main()
