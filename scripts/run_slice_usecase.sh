#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

SLICE="${1:?usage: run_slice_usecase.sh <slice.yaml> <testcase.yaml>}"
TESTCASE="${2:?usage: run_slice_usecase.sh <slice.yaml> <testcase.yaml>}"

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.apply_slice_profile "$SLICE"
PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.run_testcase "$TESTCASE" --slice "$SLICE"
