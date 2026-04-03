from __future__ import annotations

import json
import os

from tools.common import runtime_dir

FALLBACK_PROCESS_NAMES = {
    "amf": ["open5gs-amfd"],
    "ausf": ["open5gs-ausfd"],
    "gnb": ["gnb"],
    "nrf": ["open5gs-nrfd"],
    "nssf": ["open5gs-nssfd"],
    "omnetpp": ["opp_run", "omnetpp_sitl"],
    "pcf": ["open5gs-pcfd"],
    "smf": ["open5gs-smfd"],
    "udm": ["open5gs-udmd"],
    "udr": ["open5gs-udrd"],
    "ue": ["srsue"],
    "upf": ["open5gs-upfd"],
}


def process_exists(names: list[str]) -> bool:
    return any(os.system(f'pgrep -x "{name}" > /dev/null 2>&1') == 0 for name in names)


def main() -> None:
    pid_dir = runtime_dir() / "pids"
    summary: dict[str, str] = {}
    if pid_dir.exists():
        for pid_file in sorted(pid_dir.glob("*.pid")):
            try:
                pid = int(pid_file.read_text(encoding="utf-8").strip())
                os.kill(pid, 0)
                summary[pid_file.stem] = "running"
            except PermissionError:
                summary[pid_file.stem] = "running"
            except Exception:
                fallback_names = FALLBACK_PROCESS_NAMES.get(pid_file.stem)
                summary[pid_file.stem] = "running" if fallback_names and process_exists(fallback_names) else "stale"
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
