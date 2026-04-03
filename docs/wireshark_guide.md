# Wireshark Guide

Capture locations:

- `N2`: NGAP/NAS signaling where visible on loopback or bind interface
- `N3`: GTP-U path between gNB and UPF
- `UPF-DN`: user-plane toward the TUN/data network side
- `host-bridge`: generic all-interface troubleshooting capture

Recommended display filters:

- `icmp`
- `udp`
- `tcp`
- `gtp`
- `ngap || sctp`
- `icmp || udp.port == 2152`

Notes:

- NAS visibility depends on where encapsulation is exposed by the chosen stack
- GTP-U is most visible on the N3 path
- correlate timestamps with `outputs/logs/` and the testcase report name

Workflow:

1. start capture with the testcase name
2. run the testcase
3. stop capture
4. open the resulting `pcapng` in Wireshark
5. run `python3 tools/pcap_analyzer.py outputs/pcap`

Live integration beyond offline workflow is `TODO(version-check)`.
