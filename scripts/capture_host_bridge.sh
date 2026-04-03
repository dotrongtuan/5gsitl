#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/capture_common.sh"

capture_file host-bridge "${1:-any}" "${2:-manual}"
