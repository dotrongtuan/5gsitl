#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/capture_common.sh"

TESTCASE="${1:-manual}"
capture_file all any "$TESTCASE"
