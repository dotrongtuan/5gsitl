#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

if [[ ! -d "${OMNETPP_ROOT:-}" ]]; then
  die "OMNETPP_ROOT is not set to a valid OMNeT++ installation."
fi

if ! find "${PROJECT_ROOT}/omnetpp/out" -name 'libomnetpp_sitl.so' -o -name 'libomnetpp_sitl.dylib' -o -name 'omnetpp_sitl.dll' 2>/dev/null | grep -q .; then
  bash "${PROJECT_ROOT}/omnetpp/build.sh"
fi

nohup bash -lc "cd '${PROJECT_ROOT}/omnetpp' && set +u && source '${OMNETPP_ROOT}/setenv' && set -u && LIB=\$(find out -name 'omnetpp_sitl*' | head -n 1) && opp_run -u Qtenv -n ned -l \"\${LIB}\" ${OMNETPP_INI:-simulations/omnetpp.ini}" \
  > "${PROJECT_ROOT}/outputs/logs/omnetpp.stdout.log" 2>&1 &
write_pid omnetpp "$!"

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.topology_state_exporter component omnetpp --state up >/dev/null
log "OMNeT++ GUI launched."
