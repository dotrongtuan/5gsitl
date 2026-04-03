# Test Plan

Baseline checks:

- core daemons start
- gNB process starts
- UE process starts
- attach and IP allocation state export updates
- ping and UDP test flows complete
- pcap files are written
- reports are generated
- OMNeT++ state files are refreshed

Scenario classes:

- `nr`: SA attach and baseline connectivity
- `latency`: RTT-focused runs
- `phy`: channel impairments and scheduler stress
- `slicing`: slice-aware use-case studies

Automation hooks:

- `scripts/run_testcase.sh`
- `python3 tools/run_suite.py`
- `pytest`
