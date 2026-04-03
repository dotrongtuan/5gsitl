from __future__ import annotations

import argparse

from tools.common import load_yaml

REQUIRED = {"name", "sst", "sd", "dnn", "qos", "traffic_template", "kpi_targets", "ran_profile"}


def validate(path: str) -> dict:
    data = load_yaml(path)
    missing = sorted(REQUIRED - set(data))
    if missing:
        raise ValueError(f"Missing slice config keys: {', '.join(missing)}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    data = validate(args.path)
    print(f"valid slice profile: {data['name']}")


if __name__ == "__main__":
    main()
