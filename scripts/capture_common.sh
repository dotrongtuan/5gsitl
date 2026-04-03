#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

capture_file() {
  local label="$1"
  local iface="$2"
  local testcase="${3:-manual}"
  local stamp
  stamp="$(timestamp)"
  local out="${PROJECT_ROOT}/outputs/pcap/${testcase}_${label}_${stamp}.pcapng"
  sudo dumpcap -i "$iface" -w "$out" -b filesize:"${CAPTURE_ROTATE_MB:-250}" -b files:"${CAPTURE_ROTATE_COUNT:-8}" \
    >/dev/null 2>&1 &
  write_pid "capture-${label}" "$!"
  printf '%s\n' "$out" > "${PROJECT_ROOT}/outputs/runtime/${label}.pcap.path"
  log "Capture ${label} -> ${out}"
}
