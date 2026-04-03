from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from tools.common import load_yaml, outputs_dir

DBCTL_URL = "https://raw.githubusercontent.com/open5gs/open5gs/main/misc/db/open5gs-dbctl"


def ensure_dbctl(download_if_missing: bool = True) -> str:
    existing = shutil.which("open5gs-dbctl")
    if existing:
        return existing
    if not download_if_missing:
        raise FileNotFoundError("open5gs-dbctl not found in PATH")
    cache_dir = outputs_dir("runtime") / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / "open5gs-dbctl"
    if not target.exists():
        with urlopen(DBCTL_URL) as response:
            payload = response.read()
        target.write_bytes(payload)
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return str(target)


def build_commands(subscriber: dict, dbctl_path: str, db_uri: str) -> list[list[str]]:
    prefix = ["bash", dbctl_path, f"--db_uri={db_uri}"]
    imsi = str(subscriber["imsi"])
    key = str(subscriber["key"])
    opc = str(subscriber["opc"])
    dnn = str(subscriber.get("dnn", "internet"))
    slices = list(subscriber.get("slices") or [{"sst": 1, "sd": "000001"}])
    first = slices[0]

    commands: list[list[str]] = [prefix + ["remove", imsi]]
    commands.append(
        prefix
        + [
            "add_ue_with_slice",
            imsi,
            key,
            opc,
            dnn,
            str(first.get("sst", 1)),
            str(first.get("sd", "000001")),
        ]
    )
    for extra in slices[1:]:
        commands.append(
            prefix
            + [
                "update_slice",
                imsi,
                dnn,
                str(extra.get("sst", 1)),
                str(extra.get("sd", "000001")),
            ]
        )
    if subscriber.get("ipv4"):
        commands.append(prefix + ["static_ip", imsi, str(subscriber["ipv4"])])
    return commands


def wait_for_mongo(db_uri: str, attempts: int = 30, delay_s: float = 1.0) -> None:
    mongosh = shutil.which("mongosh")
    if not mongosh:
        return
    for _ in range(attempts):
        probe = subprocess.run(
            [mongosh, "--quiet", db_uri, "--eval", "db.runCommand({ ping: 1 })"],
            check=False,
            capture_output=True,
            text=True,
        )
        if probe.returncode == 0:
            return
        time.sleep(delay_s)
    raise RuntimeError("MongoDB did not become ready in time")


def provision(subscribers_path: str, db_uri: str, download_if_missing: bool = True, dry_run: bool = False) -> int:
    payload = load_yaml(subscribers_path)
    subscribers = payload.get("subscribers", [])
    if not isinstance(subscribers, list) or not subscribers:
        raise ValueError("subscribers.yaml must contain a non-empty 'subscribers' list")

    dbctl_path = ensure_dbctl(download_if_missing=download_if_missing)
    wait_for_mongo(db_uri)

    failures = 0
    for subscriber in subscribers:
        for command in build_commands(subscriber, dbctl_path, db_uri):
            if dry_run:
                print(" ".join(command))
                continue
            result = subprocess.run(command, check=False, capture_output=True, text=True)
            if command[-2] == "remove" and result.returncode != 0:
                continue
            if result.returncode != 0:
                failures += 1
                sys.stderr.write(result.stdout)
                sys.stderr.write(result.stderr)
                break
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision Open5GS subscribers from YAML.")
    parser.add_argument(
        "--subscribers",
        default=os.environ.get("OPEN5GS_SUBSCRIBERS_FILE", "configs/core/subscribers.yaml"),
    )
    parser.add_argument(
        "--db-uri",
        default=os.environ.get("MONGODB_URI", "mongodb://127.0.0.1/open5gs"),
    )
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    failures = provision(
        subscribers_path=args.subscribers,
        db_uri=args.db_uri,
        download_if_missing=not args.no_download,
        dry_run=args.dry_run,
    )
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
