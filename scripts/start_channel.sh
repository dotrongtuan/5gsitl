#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

PROFILE="${1:-${GNURADIO_CHANNEL_PROFILE:-${PROJECT_ROOT}/configs/channel/bypass.yaml}}"
CHANNEL_PYTHON_BIN="${CHANNEL_PYTHON_BIN:-}"

select_channel_python() {
  local candidates=()

  if [[ -n "${CHANNEL_PYTHON_BIN}" ]]; then
    candidates+=("${CHANNEL_PYTHON_BIN}")
  fi
  candidates+=("/usr/bin/python3" "python3")

  local candidate
  for candidate in "${candidates[@]}"; do
    if ! command -v "${candidate}" >/dev/null 2>&1; then
      continue
    fi
    if "${candidate}" -c "from gnuradio import gr, zeromq" >/dev/null 2>&1; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done

  die "Unable to find a Python interpreter with GNU Radio bindings for the channel emulator."
}

CHANNEL_PYTHON="$(select_channel_python)"

mkdir -p "${PROJECT_ROOT}/outputs/logs/channel"
nohup "${CHANNEL_PYTHON}" "${PROJECT_ROOT}/gnuradio/runner.py" --profile "$PROFILE" \
  > "${PROJECT_ROOT}/outputs/logs/channel/channel.stdout.log" 2>&1 &
write_pid channel "$!"

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.topology_state_exporter component channel --state up >/dev/null
log "Channel emulator started with profile $PROFILE using ${CHANNEL_PYTHON}."
