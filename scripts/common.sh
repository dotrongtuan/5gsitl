#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -f "${PROJECT_ROOT}/.env" ]]; then
  set -a
  source "${PROJECT_ROOT}/.env"
  set +a
fi

mkdir -p \
  "${PROJECT_ROOT}/outputs/logs" \
  "${PROJECT_ROOT}/outputs/pcap" \
  "${PROJECT_ROOT}/outputs/reports" \
  "${PROJECT_ROOT}/outputs/csv" \
  "${PROJECT_ROOT}/outputs/figures" \
  "${PROJECT_ROOT}/outputs/runtime/pids"

timestamp() {
  date +"%Y%m%d-%H%M%S"
}

log() {
  printf '[%s] %s\n' "$(date --iso-8601=seconds)" "$*"
}

die() {
  log "ERROR: $*"
  exit 1
}

require_bin() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required binary: $1"
}

sudo_if_needed() {
  if [[ "$(id -u)" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

write_pid() {
  local name="$1"
  local pid="$2"
  printf '%s' "$pid" > "${PROJECT_ROOT}/outputs/runtime/pids/${name}.pid"
}

kill_if_running() {
  local name="$1"
  local pid_file="${PROJECT_ROOT}/outputs/runtime/pids/${name}.pid"
  if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" >/dev/null 2>&1; then
    kill "$(cat "$pid_file")"
  fi
}
