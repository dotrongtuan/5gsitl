#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

for name in mongodb omnetpp adapter-slice adapter-testcase adapter-metrics adapter-state ue gnb channel \
  nssf pcf udr udm ausf upf smf amf nrf; do
  kill_if_running "$name" || true
done

(cd "${PROJECT_ROOT}/infra" && docker compose stop mongodb adapter-api >/dev/null 2>&1 || true)
PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.topology_state_exporter component all --state down >/dev/null || true
log "All managed components stopped."
