from __future__ import annotations

import argparse
from pathlib import Path

from tools.run_testcase import execute_testcase


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="YAML file or directory")
    args = parser.parse_args()

    target = Path(args.target)
    files = [target] if target.is_file() else sorted(target.rglob("*.yaml"))
    for testcase in files:
        print(execute_testcase(str(testcase)))


if __name__ == "__main__":
    main()
