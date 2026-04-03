#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.metrics_parser "${PROJECT_ROOT}/outputs/runtime/metrics.json"
PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.plot_latency "${PROJECT_ROOT}/outputs/csv/latency_latest.csv"
PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.pcap_analyzer "${PROJECT_ROOT}/outputs/pcap" --summary-only
log "Results exported to outputs/csv, outputs/figures, and outputs/reports."
