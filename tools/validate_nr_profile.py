from __future__ import annotations

import argparse

from tools.common import load_yaml

REQUIRED = {"name", "sa_mode", "mu", "scs_khz", "slot_ms", "scheduler_profile"}


def validate(path: str) -> dict:
    data = load_yaml(path)
    missing = sorted(REQUIRED - set(data))
    if missing:
        raise ValueError(f"Missing NR profile keys: {', '.join(missing)}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    data = validate(args.path)
    print(f"valid nr profile: {data['name']}")


if __name__ == "__main__":
    main()
