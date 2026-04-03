from __future__ import annotations

import argparse
import time

from adapters.schema import TestcaseState
from tools.common import dump_json, load_runtime_state, outputs_dir


def step() -> None:
    state = load_runtime_state()
    payload = TestcaseState(
        name=state.get("active_testcase", ""),
        scenario_class=state.get("active_scenario", ""),
        expected_kpis={},
    )
    dump_json(outputs_dir("runtime") / "omnetpp_testcase.json", payload.model_dump())


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
