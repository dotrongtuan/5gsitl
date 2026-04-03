#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

bash "${PROJECT_ROOT}/scripts/setup_host_network.sh"
bash "${PROJECT_ROOT}/scripts/start_core.sh"
sleep 3
bash "${PROJECT_ROOT}/scripts/start_gnb.sh"
sleep 2
bash "${PROJECT_ROOT}/scripts/start_ue.sh"
sleep 2
bash "${PROJECT_ROOT}/scripts/start_channel.sh"
bash "${PROJECT_ROOT}/scripts/start_adapters.sh"
if [[ -n "${OMNETPP_ROOT:-}" && -d "${OMNETPP_ROOT:-}" ]]; then
  bash "${PROJECT_ROOT}/scripts/start_omnetpp_gui.sh"
fi

log "All main components started."
