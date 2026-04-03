#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

TIMEOUT="${1:-45}"
GATEWAY="${2:-10.45.0.1}"
UE_IF="${3:-tun_srsue}"

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.attach_checker \
  --namespace "${UE_NAMESPACE:-ue1}" \
  --interface "${UE_IF}" \
  --gateway "${GATEWAY}" \
  --timeout "${TIMEOUT}"
