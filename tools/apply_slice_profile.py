from __future__ import annotations

import argparse
from pathlib import Path

from tools.common import dump_json, outputs_dir, record_event, update_runtime_state
from tools.validate_slice_config import validate


def apply_slice(path: str) -> dict:
    data = validate(path)
    dump_json(outputs_dir("runtime") / "active_slice.json", data)
    update_runtime_state(active_slice=data["name"])
    record_event("slice.apply", f"Applied slice {data['name']}", profile=str(Path(path)))
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    data = apply_slice(args.path)
    print(f"applied slice: {data['name']}")


if __name__ == "__main__":
    main()
