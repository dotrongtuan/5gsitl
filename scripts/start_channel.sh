#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

PROFILE="${1:-${GNURADIO_CHANNEL_PROFILE:-${PROJECT_ROOT}/configs/channel/bypass.yaml}}"
require_bin python3

mkdir -p "${PROJECT_ROOT}/outputs/logs/channel"
nohup python3 "${PROJECT_ROOT}/gnuradio/runner.py" --profile "$PROFILE" \
  > "${PROJECT_ROOT}/outputs/logs/channel/channel.stdout.log" 2>&1 &
write_pid channel "$!"

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.topology_state_exporter component channel --state up >/dev/null
log "Channel emulator started with profile $PROFILE."
