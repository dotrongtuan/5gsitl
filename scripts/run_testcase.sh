#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

TESTCASE="${1:?usage: run_testcase.sh <testcase.yaml>}"
PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.run_testcase "$TESTCASE"
