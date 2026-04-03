from __future__ import annotations

import argparse
import time

from adapters.schema import SliceState
from tools.common import dump_json, load_json, outputs_dir


def step() -> None:
    data = load_json(outputs_dir("runtime") / "active_slice.json", {})
    payload = SliceState(
        name=data.get("name", ""),
        sst=data.get("sst", 1),
        sd=data.get("sd", ""),
        dnn=data.get("dnn", ""),
    )
    dump_json(outputs_dir("runtime") / "omnetpp_slice.json", payload.model_dump())


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
