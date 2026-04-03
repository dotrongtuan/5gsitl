#!/usr/bin/env bash
set -euo pipefail

IFACE="${1:-lo}"
DELAY_MS="${2:-0}"
LOSS_PCT="${3:-0}"
JITTER_MS="${4:-0}"

sudo tc qdisc replace dev "$IFACE" root netem delay "${DELAY_MS}ms" "${JITTER_MS}ms" loss "${LOSS_PCT}%"
echo "Applied netem to $IFACE delay=${DELAY_MS}ms jitter=${JITTER_MS}ms loss=${LOSS_PCT}%"
