from __future__ import annotations

import argparse

from tools.common import record_event, update_runtime_state


def main() -> None:
    parser = argparse.ArgumentParser(description="Update the exported OMNeT++ runtime state.")
    sub = parser.add_subparsers(dest="command", required=True)

    component_cmd = sub.add_parser("component")
    component_cmd.add_argument("name")
    component_cmd.add_argument("--state", dest="state_value", required=True)

    args = parser.parse_args()
    if args.command == "component":
        update_runtime_state(component=args.name, state_value=args.state_value)
        record_event("component.state", f"{args.name} -> {args.state_value}", component=args.name, state=args.state_value)


if __name__ == "__main__":
    main()
