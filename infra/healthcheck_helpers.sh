#!/usr/bin/env bash
set -euo pipefail

check_port() {
  local host="$1"
  local port="$2"
  timeout 2 bash -lc "cat < /dev/null > /dev/tcp/${host}/${port}" >/dev/null 2>&1
}

check_pid_file() {
  local pid_file="$1"
  [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" >/dev/null 2>&1
}
