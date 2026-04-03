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
start_mongodb

if ! PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.provision_subscribers \
  --subscribers "${OPEN5GS_SUBSCRIBERS_FILE:-${PROJECT_ROOT}/configs/core/subscribers.yaml}" \
  --db-uri "${MONGODB_URI:-mongodb://127.0.0.1/open5gs}"; then
  log "WARNING: subscriber provisioning failed. Continuing with existing MongoDB data."
fi

nohup open5gs-nrfd -c "${PROJECT_ROOT}/configs/core/nrf.yaml" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/nrf.stdout.log" 2>&1 &
write_pid nrf "$!"
nohup open5gs-amfd -c "${PROJECT_ROOT}/configs/core/amf.yaml" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/amf.stdout.log" 2>&1 &
write_pid amf "$!"
nohup open5gs-smfd -c "${PROJECT_ROOT}/configs/core/smf.yaml" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/smf.stdout.log" 2>&1 &
write_pid smf "$!"
nohup open5gs-upfd -c "${PROJECT_ROOT}/configs/core/upf.yaml" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/upf.stdout.log" 2>&1 &
write_pid upf "$!"
nohup open5gs-ausfd -c "${PROJECT_ROOT}/configs/core/ausf.yaml" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/ausf.stdout.log" 2>&1 &
write_pid ausf "$!"
nohup open5gs-udmd -c "${PROJECT_ROOT}/configs/core/udm.yaml" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/udm.stdout.log" 2>&1 &
write_pid udm "$!"
nohup open5gs-udrd -c "${PROJECT_ROOT}/configs/core/udr.yaml" \
  > "${PROJECT_ROOT}/outputs/logs/open5gs/udr.stdout.log" 2>&1 &
write_pid udr "$!"

if command -v open5gs-pcfd >/dev/null 2>&1; then
  nohup open5gs-pcfd -c "${PROJECT_ROOT}/configs/core/pcf.yaml" \
    > "${PROJECT_ROOT}/outputs/logs/open5gs/pcf.stdout.log" 2>&1 &
  write_pid pcf "$!"
fi

if command -v open5gs-nssfd >/dev/null 2>&1; then
  nohup open5gs-nssfd -c "${PROJECT_ROOT}/configs/core/nssf.yaml" \
    > "${PROJECT_ROOT}/outputs/logs/open5gs/nssf.stdout.log" 2>&1 &
  write_pid nssf "$!"
fi

PYTHONPATH="${PROJECT_ROOT}" python3 -m tools.topology_state_exporter component core --state up >/dev/null
log "Open5GS core started."
