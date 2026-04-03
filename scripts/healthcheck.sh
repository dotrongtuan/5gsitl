#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
source "${PROJECT_ROOT}/infra/healthcheck_helpers.sh"

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.session_checker

check_process_name open5gs-amfd && log "AMF process running" || log "AMF process missing"
check_process_name gnb && log "gNB process running" || log "gNB process missing"
check_process_name srsue && log "UE process running" || log "UE process missing"

check_port 127.0.0.10 7777 && log "NRF SBI reachable" || log "NRF SBI not reachable"
check_port 10.10.0.10 38412 && log "AMF NGAP reachable" || log "AMF NGAP not reachable"
check_port 127.0.0.1 "${ADAPTER_HTTP_PORT:-18080}" && log "Adapter HTTP reachable" || log "Adapter HTTP not reachable"
