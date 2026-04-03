from __future__ import annotations

import argparse
import time

from tools.common import dump_json, env_path, load_json, outputs_dir


def step() -> None:
    payload = load_json(env_path("METRICS_FILE", "outputs/runtime/metrics.json"), {})
    dump_json(outputs_dir("runtime") / "omnetpp_metrics.json", payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.once:
        step()
        return
    while True:
        step()
        time.sleep(1.0)


if __name__ == "__main__":
    main()
