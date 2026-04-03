from __future__ import annotations

import argparse
import json
import re
import subprocess
import time

from tools.common import record_event, update_runtime_state

INET_RE = re.compile(r"\binet (?P<ip>\d+\.\d+\.\d+\.\d+/\d+)\b")


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def namespace_exists(namespace: str) -> bool:
    return _run(["ip", "netns", "list"]).returncode == 0 and namespace in _run(["ip", "netns", "list"]).stdout


def detect_ue_ip(namespace: str, interface: str) -> str:
    result = _run(["sudo", "ip", "netns", "exec", namespace, "ip", "-4", "addr", "show", interface])
    if result.returncode != 0:
        return ""
    match = INET_RE.search(result.stdout)
    return match.group("ip").split("/")[0] if match else ""


def gateway_reachable(namespace: str, gateway: str) -> bool:
    result = _run(["sudo", "ip", "netns", "exec", namespace, "ping", "-c", "1", "-W", "1", gateway])
    return result.returncode == 0


def wait_for_attach(namespace: str, interface: str, gateway: str, timeout_s: int) -> dict[str, str | bool]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        ue_ip = detect_ue_ip(namespace, interface)
        if ue_ip and gateway_reachable(namespace, gateway):
            update_runtime_state(attach_state="attached", ue_ip=ue_ip)
            record_event("ue.attach", f"UE attached with IP {ue_ip}", namespace=namespace, interface=interface, gateway=gateway)
            return {"attached": True, "ue_ip": ue_ip}
        time.sleep(1.0)
    update_runtime_state(attach_state="failed")
    record_event("ue.attach", "UE attach check timed out", namespace=namespace, interface=interface, gateway=gateway, timeout_s=timeout_s)
    return {"attached": False, "ue_ip": ""}


def main() -> None:
    parser = argparse.ArgumentParser(description="Wait for UE attach evidence in the namespace and TUN interface.")
    parser.add_argument("--namespace", default="ue1")
    parser.add_argument("--interface", default="tun_srsue")
    parser.add_argument("--gateway", default="10.45.0.1")
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()
    print(json.dumps(wait_for_attach(args.namespace, args.interface, args.gateway, args.timeout)))


if __name__ == "__main__":
    main()
