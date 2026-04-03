#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_bin "${SRSRAN_UE_BIN:-srsue}"
mkdir -p "${PROJECT_ROOT}/outputs/logs/ue"

if ! sudo_if_needed ip netns list | grep -q "${UE_NAMESPACE:-ue1}"; then
  sudo_if_needed ip netns add "${UE_NAMESPACE:-ue1}"
fi

if [[ "$(id -u)" -eq 0 ]]; then
  nohup "${SRSRAN_UE_BIN:-srsue}" "${SRSRAN_UE_CONFIG:-${PROJECT_ROOT}/configs/ue/ue_zmq.conf}" \
    > "${PROJECT_ROOT}/outputs/logs/ue/ue.stdout.log" 2>&1 &
else
  nohup sudo "${SRSRAN_UE_BIN:-srsue}" "${SRSRAN_UE_CONFIG:-${PROJECT_ROOT}/configs/ue/ue_zmq.conf}" \
    > "${PROJECT_ROOT}/outputs/logs/ue/ue.stdout.log" 2>&1 &
fi
write_pid ue "$!"

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.topology_state_exporter component ue --state up >/dev/null
log "UE started."
