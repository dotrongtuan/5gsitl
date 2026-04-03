#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

STAMP="$(timestamp)"
OUT="${PROJECT_ROOT}/outputs/reports/logbundle_${STAMP}.tar.gz"
tar -czf "$OUT" -C "${PROJECT_ROOT}" outputs/logs outputs/runtime || true
log "Collected logs into $OUT"
