from pathlib import Path

from scapy.all import ICMP, IP, wrpcap

from tools.pcap_analyzer import analyze


def test_pcap_analyzer_extracts_flows(tmp_path: Path) -> None:
    pcap = tmp_path / "sample.pcap"
    wrpcap(
        str(pcap),
        [
            IP(src="10.0.0.1", dst="10.0.0.2") / ICMP(type=8, id=1, seq=1),
            IP(src="10.0.0.2", dst="10.0.0.1") / ICMP(type=0, id=1, seq=1),
        ],
    )
    result = analyze(pcap)
    assert result["packet_count"] == 2
    assert result["flow_count"] >= 1
