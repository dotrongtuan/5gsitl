from __future__ import annotations

import argparse

from tools.common import set_component_state


def main() -> None:
    parser = argparse.ArgumentParser(description="Update the exported OMNeT++ runtime state.")
    sub = parser.add_subparsers(dest="command", required=True)

    component_cmd = sub.add_parser("component")
    component_cmd.add_argument("name")
    component_cmd.add_argument("--state", dest="state_value", required=True)

    args = parser.parse_args()
    if args.command == "component":
        set_component_state(args.name, args.state_value)


if __name__ == "__main__":
    main()
