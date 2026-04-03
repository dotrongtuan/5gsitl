# Observability

Artifacts:

- logs: `outputs/logs/`
- runtime state: `outputs/runtime/`
- pcaps: `outputs/pcap/`
- CSV: `outputs/csv/`
- figures: `outputs/figures/`
- reports: `outputs/reports/`

Key producers:

- `tools/topology_state_exporter.py`
- adapter processes under `adapters/`
- `tools/latency_monitor.py`
- `tools/metrics_parser.py`
- `tools/pcap_analyzer.py`

Timestamp strategy:

- ISO-8601 for JSON/event records
- filename-friendly local timestamps in shell capture/output bundles

The OMNeT++ runtime view is intentionally fed from the same exported state that the reporting tools consume.
