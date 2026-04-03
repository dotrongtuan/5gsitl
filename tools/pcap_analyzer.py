from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Iterable

from scapy.all import ICMP, IP, PcapReader, TCP, UDP

from tools.common import dump_json, outputs_dir


def iter_pcaps(target: Path) -> Iterable[Path]:
    if target.is_dir():
        yield from sorted(target.glob("*.pcap*"))
    else:
        yield target


def analyze(target: Path) -> dict:
    packets = 0
    flows: Counter[str] = Counter()
    first_ts = None
    last_ts = None
    echo_requests: dict[tuple[int, int], float] = {}
    rtts: list[float] = []

    for pcap in iter_pcaps(target):
        with PcapReader(str(pcap)) as reader:
            for packet in reader:
                packets += 1
                if first_ts is None:
                    first_ts = float(packet.time)
                last_ts = float(packet.time)
                if IP not in packet:
                    continue
                ip = packet[IP]
                proto = "OTHER"
                if TCP in packet:
                    proto = f"TCP/{packet[TCP].sport}->{packet[TCP].dport}"
                elif UDP in packet:
                    proto = f"UDP/{packet[UDP].sport}->{packet[UDP].dport}"
                elif ICMP in packet:
                    proto = f"ICMP/{packet[ICMP].type}"
                    if packet[ICMP].type == 8:
                        echo_requests[(packet[ICMP].id, packet[ICMP].seq)] = float(packet.time)
                    elif packet[ICMP].type == 0:
                        key = (packet[ICMP].id, packet[ICMP].seq)
                        if key in echo_requests:
                            rtts.append((float(packet.time) - echo_requests.pop(key)) * 1000.0)
                flows[f"{ip.src}->{ip.dst} {proto}"] += 1

    total_echo = len(echo_requests) + len(rtts)
    loss_pct = round((len(echo_requests) / max(total_echo, 1)) * 100.0, 3) if total_echo else 0.0
    return {
        "packet_count": packets,
        "first_timestamp": first_ts,
        "last_timestamp": last_ts,
        "flow_count": len(flows),
        "flows": dict(flows.most_common(20)),
        "rtt_approx_ms": {
            "samples": len(rtts),
            "avg": round(sum(rtts) / len(rtts), 3) if rtts else 0.0,
            "max": round(max(rtts), 3) if rtts else 0.0,
        },
        "packet_loss_estimate_pct": loss_pct,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()

    target = Path(args.target)
    result = analyze(target)
    stem = target.stem if target.is_file() else "pcap_summary"
    dump_json(outputs_dir("reports") / f"{stem}.pcap.json", result)

    csv_path = outputs_dir("csv") / f"{stem}.pcap.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["flow", "count"])
        for flow, count in result["flows"].items():
            writer.writerow([flow, count])

    print(result["packet_count"] if args.summary_only else result)


if __name__ == "__main__":
    main()
