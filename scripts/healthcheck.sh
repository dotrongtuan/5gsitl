#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
source "${PROJECT_ROOT}/infra/healthcheck_helpers.sh"

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.session_checker

check_pid_file "${PROJECT_ROOT}/outputs/runtime/pids/amf.pid" && log "AMF pid OK" || log "AMF pid missing"
check_pid_file "${PROJECT_ROOT}/outputs/runtime/pids/gnb.pid" && log "gNB pid OK" || log "gNB pid missing"
check_pid_file "${PROJECT_ROOT}/outputs/runtime/pids/ue.pid" && log "UE pid OK" || log "UE pid missing"

check_port 127.0.0.10 7777 && log "NRF SBI reachable" || log "NRF SBI not reachable"
check_port 127.0.0.1 "${ADAPTER_HTTP_PORT:-18080}" && log "Adapter HTTP reachable" || log "Adapter HTTP not reachable"
