from __future__ import annotations

import json
import os

from tools.common import runtime_dir


def main() -> None:
    pid_dir = runtime_dir() / "pids"
    summary: dict[str, str] = {}
    if pid_dir.exists():
        for pid_file in sorted(pid_dir.glob("*.pid")):
            try:
                pid = int(pid_file.read_text(encoding="utf-8").strip())
                os.kill(pid, 0)
                summary[pid_file.stem] = "running"
            except Exception:
                summary[pid_file.stem] = "stale"
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
