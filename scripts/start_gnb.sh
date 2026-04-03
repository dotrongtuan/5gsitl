#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_bin "${SRSRAN_GNB_BIN:-gnb}"
mkdir -p "${PROJECT_ROOT}/outputs/logs/gnb"

GNB_LIB_PATH="/usr/local/lib:/usr/local/lib64:${LD_LIBRARY_PATH:-}"
if [[ "$(id -u)" -eq 0 ]]; then
  nohup env LD_LIBRARY_PATH="${GNB_LIB_PATH}" "${SRSRAN_GNB_BIN:-gnb}" -c "${SRSRAN_GNB_CONFIG:-${PROJECT_ROOT}/configs/gnb/gnb_zmq.yaml}" \
    > "${PROJECT_ROOT}/outputs/logs/gnb/gnb.stdout.log" 2>&1 &
else
  nohup sudo env LD_LIBRARY_PATH="${GNB_LIB_PATH}" "${SRSRAN_GNB_BIN:-gnb}" -c "${SRSRAN_GNB_CONFIG:-${PROJECT_ROOT}/configs/gnb/gnb_zmq.yaml}" \
    > "${PROJECT_ROOT}/outputs/logs/gnb/gnb.stdout.log" 2>&1 &
fi
write_pid gnb "$!"

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.topology_state_exporter component gnb --state up >/dev/null
log "gNB started."
