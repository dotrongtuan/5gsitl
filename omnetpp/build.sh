#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${OMNETPP_ROOT:-}" ]]; then
  echo "OMNETPP_ROOT is required"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
source "${OMNETPP_ROOT}/setenv"
opp_makemake -f --deep -O out -o omnetpp_sitl
make -j"$(nproc)" MODE=release
