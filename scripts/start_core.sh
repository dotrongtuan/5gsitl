#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_bin python3
require_bin open5gs-nrfd
require_bin open5gs-amfd
require_bin open5gs-smfd
require_bin open5gs-upfd
require_bin open5gs-ausfd
require_bin open5gs-udmd
require_bin open5gs-udrd

is_compat_profile() {
  case "${SRSRAN_UE_CONFIG:-}" in
    *"/configs/ue/ue_zmq_compat.conf"|*"\\configs\\ue\\ue_zmq_compat.conf") return 0 ;;
  esac
  case "${SRSRAN_GNB_CONFIG:-}" in
    *"/configs/gnb/gnb_zmq_compat.yaml"|*"\\configs\\gnb\\gnb_zmq_compat.yaml") return 0 ;;
  esac
  return 1
}

NRF_CONFIG="${OPEN5GS_NRF_CONFIG:-${PROJECT_ROOT}/configs/core/nrf.yaml}"
AMF_CONFIG="${OPEN5GS_AMF_CONFIG:-${PROJECT_ROOT}/configs/core/amf.yaml}"
SMF_CONFIG="${OPEN5GS_SMF_CONFIG:-${PROJECT_ROOT}/configs/core/smf.yaml}"
UPF_CONFIG="${OPEN5GS_UPF_CONFIG:-${PROJECT_ROOT}/configs/core/upf.yaml}"
AUSF_CONFIG="${OPEN5GS_AUSF_CONFIG:-${PROJECT_ROOT}/configs/core/ausf.yaml}"
UDM_CONFIG="${OPEN5GS_UDM_CONFIG:-${PROJECT_ROOT}/configs/core/udm.yaml}"
UDR_CONFIG="${OPEN5GS_UDR_CONFIG:-${PROJECT_ROOT}/configs/core/udr.yaml}"
PCF_CONFIG="${OPEN5GS_PCF_CONFIG:-${PROJECT_ROOT}/configs/core/pcf.yaml}"
NSSF_CONFIG="${OPEN5GS_NSSF_CONFIG:-${PROJECT_ROOT}/configs/core/nssf.yaml}"
SUBSCRIBERS_FILE="${OPEN5GS_SUBSCRIBERS_FILE:-${PROJECT_ROOT}/configs/core/subscribers.yaml}"
ENABLE_PCF="${OPEN5GS_ENABLE_PCF:-1}"
ENABLE_NSSF="${OPEN5GS_ENABLE_NSSF:-1}"
STRICT_SUBSCRIBER_PROVISIONING="${OPEN5GS_STRICT_SUBSCRIBER_PROVISIONING:-0}"

if is_compat_profile; then
  [[ -z "${OPEN5GS_AMF_CONFIG:-}" ]] && AMF_CONFIG="${PROJECT_ROOT}/configs/core/amf_compat.yaml"
  [[ -z "${OPEN5GS_SMF_CONFIG:-}" ]] && SMF_CONFIG="${PROJECT_ROOT}/configs/core/smf_compat.yaml"
  [[ -z "${OPEN5GS_SUBSCRIBERS_FILE:-}" ]] && SUBSCRIBERS_FILE="${PROJECT_ROOT}/configs/core/subscribers_compat.yaml"
  ENABLE_PCF="${OPEN5GS_ENABLE_PCF:-1}"
  ENABLE_NSSF="${OPEN5GS_ENABLE_NSSF:-0}"
  STRICT_SUBSCRIBER_PROVISIONING="${OPEN5GS_STRICT_SUBSCRIBER_PROVISIONING:-1}"
  log "Using compatibility Open5GS core profile."
fi

stop_packaged_open5gs_services() {
  if ! command -v systemctl >/dev/null 2>&1; then
    return 0
  fi

  for service in \
    open5gs-nrfd open5gs-amfd open5gs-smfd open5gs-upfd open5gs-ausfd \
    open5gs-udmd open5gs-udrd open5gs-pcfd open5gs-nssfd; do
    sudo_if_needed systemctl stop "${service}" >/dev/null 2>&1 || true
  done
}

stop_existing_open5gs_processes() {
  for proc in \
    open5gs-nrfd open5gs-amfd open5gs-smfd open5gs-upfd open5gs-ausfd \
    open5gs-udmd open5gs-udrd open5gs-pcfd open5gs-nssfd; do
    sudo_if_needed pkill -x "${proc}" >/dev/null 2>&1 || true
  done
}

start_mongodb() {
  if command -v mongod >/dev/null 2>&1; then
    if command -v systemctl >/dev/null 2>&1; then
      sudo_if_needed systemctl enable mongod >/dev/null 2>&1 || true
      sudo_if_needed systemctl start mongod >/dev/null 2>&1 || true
      if sudo_if_needed systemctl is-active --quiet mongod; then
        log "Using system MongoDB service."
        return 0
      fi
    fi
    mkdir -p "${PROJECT_ROOT}/outputs/runtime/mongodb"
    nohup mongod --dbpath "${PROJECT_ROOT}/outputs/runtime/mongodb" \
      > "${PROJECT_ROOT}/outputs/logs/open5gs/mongodb.stdout.log" 2>&1 &
    write_pid mongodb "$!"
    log "Using local mongod process."
    return 0
  fi

  if command -v docker >/dev/null 2>&1; then
    sudo_if_needed docker compose -f "${PROJECT_ROOT}/infra/docker-compose.yml" up -d mongodb
    log "Using Docker MongoDB container."
    return 0
  fi

  die "MongoDB is unavailable. Install mongod or docker."
}

mkdir -p "${PROJECT_ROOT}/outputs/logs/open5gs"
rm -f "${PROJECT_ROOT}/outputs/logs/open5gs/"*.log "${PROJECT_ROOT}/outputs/logs/open5gs/"*.stdout.log 2>/dev/null || true
stop_packaged_open5gs_services
stop_existing_open5gs_processes
start_mongodb

log "Open5GS config selection: AMF=${AMF_CONFIG} SMF=${SMF_CONFIG} SUBSCRIBERS=${SUBSCRIBERS_FILE} PCF=${ENABLE_PCF} NSSF=${ENABLE_NSSF}"

if ! PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.provision_subscribers \
  --subscribers "${SUBSCRIBERS_FILE}" \
  --db-uri "${MONGODB_URI:-mongodb://127.0.0.1/open5gs}"; then
  if [[ "${STRICT_SUBSCRIBER_PROVISIONING}" == "1" ]]; then
    die "Subscriber provisioning failed for the selected Open5GS profile."
  fi
  log "WARNING: subscriber provisioning failed. Continuing with existing MongoDB data."
fi

nohup open5gs-nrfd -c "${NRF_CONFIG}" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/nrf.stdout.log" 2>&1 &
write_pid nrf "$!"
nohup open5gs-amfd -c "${AMF_CONFIG}" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/amf.stdout.log" 2>&1 &
write_pid amf "$!"
nohup open5gs-smfd -c "${SMF_CONFIG}" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/smf.stdout.log" 2>&1 &
write_pid smf "$!"
nohup open5gs-upfd -c "${UPF_CONFIG}" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/upf.stdout.log" 2>&1 &
write_pid upf "$!"
nohup open5gs-ausfd -c "${AUSF_CONFIG}" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/ausf.stdout.log" 2>&1 &
write_pid ausf "$!"
nohup open5gs-udmd -c "${UDM_CONFIG}" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/udm.stdout.log" 2>&1 &
write_pid udm "$!"
nohup open5gs-udrd -c "${UDR_CONFIG}" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/udr.stdout.log" 2>&1 &
write_pid udr "$!"

if [[ "${ENABLE_PCF}" == "1" ]] && command -v open5gs-pcfd >/dev/null 2>&1; then
  nohup open5gs-pcfd -c "${PCF_CONFIG}" \
    > "${PROJECT_ROOT}/outputs/logs/open5gs/pcf.stdout.log" 2>&1 &
  write_pid pcf "$!"
fi

if [[ "${ENABLE_NSSF}" == "1" ]] && command -v open5gs-nssfd >/dev/null 2>&1; then
  nohup open5gs-nssfd -c "${NSSF_CONFIG}" \
    > "${PROJECT_ROOT}/outputs/logs/open5gs/nssf.stdout.log" 2>&1 &
  write_pid nssf "$!"
fi

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.topology_state_exporter component core --state up >/dev/null
log "Open5GS core started."
