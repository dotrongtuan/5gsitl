#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

for name in capture-all capture-n2 capture-n3 capture-upf-dn capture-host-bridge; do
  kill_if_running "$name" || true
done

log "Capture processes stopped."
