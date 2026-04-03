#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

PROFILE="${1:-${PROJECT_ROOT}/configs/nr_profiles/default_mu1_30k.yaml}"
PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.run_nr_experiment "$PROFILE"
