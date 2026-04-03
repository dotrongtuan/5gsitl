#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

TARGET="${1:-10.45.0.1}"
DURATION="${2:-10}"
BITRATE="${3:-5M}"

iperf3 -s -D -I "${PROJECT_ROOT}/outputs/runtime/pids/iperf-server.pid" >/dev/null 2>&1 || true
sudo_if_needed ip netns exec "${UE_NAMESPACE:-ue1}" iperf3 -u -c "$TARGET" -b "$BITRATE" -t "$DURATION" \
  | tee "${PROJECT_ROOT}/outputs/logs/udp-latency-test.log"
