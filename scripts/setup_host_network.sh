#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_bin ip

sudo_if_needed bash "${PROJECT_ROOT}/infra/host_tuning.sh"
sudo_if_needed bash "${PROJECT_ROOT}/infra/network_setup.sh"
sudo_if_needed bash "${PROJECT_ROOT}/infra/nat_forwarding.sh"

if ! ip netns list | grep -q "${UE_NAMESPACE:-ue1}"; then
  sudo_if_needed ip netns add "${UE_NAMESPACE:-ue1}"
fi

log "Host network setup complete."
