#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${OMNETPP_ROOT:-}" ]]; then
  echo "OMNETPP_ROOT is required"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# OMNeT++'s setenv script is not fully nounset-safe, so source it with `set +u`.
set +u
source "${OMNETPP_ROOT}/setenv"
set -u

if ! command -v opp_makemake >/dev/null 2>&1; then
  echo "OMNeT++ tools are not built yet. Building OMNeT++ runtime first..."
  (
    cd "${OMNETPP_ROOT}"
    ./configure
    make -j"$(nproc)"
  )
  set +u
  source "${OMNETPP_ROOT}/setenv"
  set -u
fi

opp_makemake -f --deep -O out -o omnetpp_sitl
make -j"$(nproc)" MODE=release
