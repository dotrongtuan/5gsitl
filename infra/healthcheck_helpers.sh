#!/usr/bin/env bash
set -euo pipefail

check_port() {
  local host="$1"
  local port="$2"
  timeout 2 bash -lc "cat < /dev/null > /dev/tcp/${host}/${port}" >/dev/null 2>&1
}

check_pid_file() {
  local pid_file="$1"
  [[ -f "$pid_file" ]] && ps -p "$(cat "$pid_file")" >/dev/null 2>&1
}

check_process_name() {
  local name="$1"
  pgrep -x "$name" >/dev/null 2>&1
}

check_socket_listener() {
  local pattern="$1"
  ss -lnH 2>/dev/null | grep -q "$pattern"
}
