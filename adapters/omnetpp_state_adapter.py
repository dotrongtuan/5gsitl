from __future__ import annotations

import argparse
import time

from adapters.file_state_adapter import snapshot_files
from tools.common import dump_json, outputs_dir, update_runtime_state


def step() -> None:
    payload = snapshot_files()["state"]
    dump_json(outputs_dir("runtime") / "omnetpp_state.json", payload)
    update_runtime_state(component="adapters", state_value="up")


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
