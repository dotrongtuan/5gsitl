#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

mkdir -p "${PROJECT_ROOT}/outputs/logs/adapters"

nohup env PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.event_bus serve \
  --host "${ADAPTER_HTTP_HOST:-127.0.0.1}" \
  --port "${ADAPTER_HTTP_PORT:-18080}" \
  > "${PROJECT_ROOT}/outputs/logs/adapters/event_bus.log" 2>&1 &
write_pid adapter-api "$!"

nohup env PYTHONPATH="${PROJECT_ROOT}" python3 -m adapters.omnetpp_state_adapter \
  > "${PROJECT_ROOT}/outputs/logs/adapters/state_adapter.log" 2>&1 &
write_pid adapter-state "$!"
nohup env PYTHONPATH="${PROJECT_ROOT}" python3 -m adapters.omnetpp_metrics_adapter \
  > "${PROJECT_ROOT}/outputs/logs/adapters/metrics_adapter.log" 2>&1 &
write_pid adapter-metrics "$!"
nohup env PYTHONPATH="${PROJECT_ROOT}" python3 -m adapters.omnetpp_testcase_adapter \
  > "${PROJECT_ROOT}/outputs/logs/adapters/testcase_adapter.log" 2>&1 &
write_pid adapter-testcase "$!"
nohup env PYTHONPATH="${PROJECT_ROOT}" python3 -m adapters.omnetpp_slice_adapter \
  > "${PROJECT_ROOT}/outputs/logs/adapters/slice_adapter.log" 2>&1 &
write_pid adapter-slice "$!"

log "Adapters started."
