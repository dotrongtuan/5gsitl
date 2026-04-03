from __future__ import annotations

import argparse
from pathlib import Path

from tools.common import dump_json, outputs_dir, record_event, update_runtime_state
from tools.validate_nr_profile import validate


def apply_nr_profile(path: str) -> dict:
    data = validate(path)
    dump_json(outputs_dir("runtime") / "active_nr_profile.json", data)
    update_runtime_state(nr_profile=data["name"])
    record_event("nr.profile", f"Applied NR profile {data['name']}", profile=str(Path(path)))
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    data = apply_nr_profile(args.path)
    print(f"applied nr profile: {data['name']}")


if __name__ == "__main__":
    main()
