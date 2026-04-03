#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

COUNT="${1:-10}"
TARGET="${2:-10.45.0.1}"
sudo_if_needed ip netns exec "${UE_NAMESPACE:-ue1}" ping -c "$COUNT" "$TARGET" | tee "${PROJECT_ROOT}/outputs/logs/ping-test.log"
