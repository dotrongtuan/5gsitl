#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/capture_common.sh"

capture_file upf-dn "${1:-ogstun}" "${2:-manual}"
