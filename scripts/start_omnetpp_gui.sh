#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

if [[ ! -d "${OMNETPP_ROOT:-}" ]]; then
  die "OMNETPP_ROOT is not set to a valid OMNeT++ installation."
fi

if ! find "${PROJECT_ROOT}/omnetpp/out" -type f \( -name 'omnetpp_sitl' -o -name 'omnetpp_sitl.exe' \) 2>/dev/null | grep -q .; then
  bash "${PROJECT_ROOT}/omnetpp/build.sh"
fi

nohup bash -lc "cd '${PROJECT_ROOT}/omnetpp' && set +u && source '${OMNETPP_ROOT}/setenv' && set -u && BIN=\$(find out -type f \( -name 'omnetpp_sitl' -o -name 'omnetpp_sitl.exe' \) | head -n 1) && \"\${BIN}\" -u Qtenv -n ned ${OMNETPP_INI:-simulations/omnetpp.ini}" \
  > "${PROJECT_ROOT}/outputs/logs/omnetpp.stdout.log" 2>&1 &
write_pid omnetpp "$!"

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.topology_state_exporter component omnetpp --state up >/dev/null
log "OMNeT++ GUI launched."
