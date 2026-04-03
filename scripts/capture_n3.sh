#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/capture_common.sh"

capture_file n3 "${1:-lo}" "${2:-manual}"
