#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

COMPONENT="${1:?usage: restart_component.sh <core|gnb|ue|channel|omnetpp|adapters>}"

case "$COMPONENT" in
  core) bash "${PROJECT_ROOT}/scripts/start_core.sh" ;;
  gnb) kill_if_running gnb || true; bash "${PROJECT_ROOT}/scripts/start_gnb.sh" ;;
  ue) kill_if_running ue || true; bash "${PROJECT_ROOT}/scripts/start_ue.sh" ;;
  channel) kill_if_running channel || true; bash "${PROJECT_ROOT}/scripts/start_channel.sh" ;;
  omnetpp) kill_if_running omnetpp || true; bash "${PROJECT_ROOT}/scripts/start_omnetpp_gui.sh" ;;
  adapters) bash "${PROJECT_ROOT}/scripts/start_adapters.sh" ;;
  *) die "Unknown component $COMPONENT" ;;
esac
