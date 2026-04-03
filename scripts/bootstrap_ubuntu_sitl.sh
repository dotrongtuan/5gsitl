#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

if [[ "$(uname -s)" != "Linux" ]]; then
  die "This bootstrap script must be run inside Ubuntu Linux or WSL Ubuntu."
fi

if [[ ! -f /etc/os-release ]]; then
  die "Unable to detect Linux distribution."
fi

source /etc/os-release
if [[ "${ID:-}" != "ubuntu" ]]; then
  die "Unsupported distro: ${ID:-unknown}. Use Ubuntu 22.04 or 24.04."
fi

UBUNTU_CODENAME="${VERSION_CODENAME:-}"
if [[ "$UBUNTU_CODENAME" != "jammy" && "$UBUNTU_CODENAME" != "noble" ]]; then
  die "Unsupported Ubuntu release: ${VERSION_ID:-unknown}. Use 22.04 or 24.04."
fi

DEBIAN_FRONTEND=noninteractive
export DEBIAN_FRONTEND

OMNETPP_VERSION="${OMNETPP_VERSION:-6.0.3}"
OMNETPP_ROOT_DEFAULT="${HOME}/opt/omnetpp-${OMNETPP_VERSION}"
OMNETPP_TARBALL="${HOME}/.cache/5g-nr-sitl/omnetpp-${OMNETPP_VERSION}-linux-x86_64.tgz"
OMNETPP_DOWNLOAD_URL="${OMNETPP_DOWNLOAD_URL:-https://github.com/omnetpp/omnetpp/releases/download/omnetpp-${OMNETPP_VERSION}/omnetpp-${OMNETPP_VERSION}-linux-x86_64.tgz}"
PYTHON_VENV="${PROJECT_ROOT}/.venv"

install_base_packages() {
  log "Installing base Ubuntu packages and build/runtime dependencies."
  sudo_if_needed apt-get update
  sudo_if_needed apt-get install -y \
    software-properties-common curl wget git ca-certificates gnupg lsb-release \
    python3 python3-pip python3-venv build-essential cmake make pkg-config \
    tcpdump tshark wireshark iproute2 iptables iperf3 jq net-tools \
    libzmq3-dev libczmq-dev gnuradio flex bison dirmngr qtbase5-dev qtchooser \
    qt5-qmake qtbase5-dev-tools libqt5opengl5-dev libfftw3-dev libsctp-dev \
    libyaml-cpp-dev libmbedtls-dev libboost-program-options-dev libconfig++-dev
}

install_open5gs() {
  log "Installing Open5GS from the official PPA."
  sudo_if_needed add-apt-repository -y ppa:open5gs/latest
  sudo_if_needed apt-get update
  sudo_if_needed apt-get install -y open5gs
}

install_mongodb() {
  log "Installing MongoDB Community and mongosh."
  curl -fsSL "https://pgp.mongodb.com/server-8.0.asc" | \
    sudo_if_needed gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor
  echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu ${UBUNTU_CODENAME}/mongodb-org/8.0 multiverse" | \
    sudo_if_needed tee /etc/apt/sources.list.d/mongodb-org-8.0.list >/dev/null
  sudo_if_needed apt-get update
  sudo_if_needed apt-get install -y mongodb-org mongodb-mongosh
  sudo_if_needed systemctl enable mongod
  sudo_if_needed systemctl start mongod
}

install_srsran_packages() {
  log "Installing srsRAN Project and srsRAN 4G packages."
  sudo_if_needed add-apt-repository -y ppa:softwareradiosystems/srsran-project
  sudo_if_needed add-apt-repository -y ppa:softwareradiosystems/srsran_4g
  sudo_if_needed apt-get update
  sudo_if_needed apt-get install -y srsran-project srsran_4g
}

install_python_env() {
  log "Creating Python virtual environment for the testbed."
  python3 -m venv "${PYTHON_VENV}"
  "${PYTHON_VENV}/bin/pip" install --upgrade pip
  "${PYTHON_VENV}/bin/pip" install -r "${PROJECT_ROOT}/requirements.txt"
}

install_omnetpp() {
  if [[ -x "${OMNETPP_ROOT_DEFAULT}/bin/opp_run" ]]; then
    log "OMNeT++ already present at ${OMNETPP_ROOT_DEFAULT}."
    return 0
  fi

  log "Installing OMNeT++ ${OMNETPP_VERSION}."
  mkdir -p "$(dirname "${OMNETPP_TARBALL}")" "$(dirname "${OMNETPP_ROOT_DEFAULT}")"
  if [[ ! -f "${OMNETPP_TARBALL}" ]]; then
    curl -L "${OMNETPP_DOWNLOAD_URL}" -o "${OMNETPP_TARBALL}"
  fi
  tar -xzf "${OMNETPP_TARBALL}" -C "$(dirname "${OMNETPP_ROOT_DEFAULT}")"
}

write_env_file() {
  log "Generating project .env with compatibility defaults."
  sed \
    -e "s#^PROJECT_ROOT=.*#PROJECT_ROOT=${PROJECT_ROOT}#" \
    -e "s#^OMNETPP_ROOT=.*#OMNETPP_ROOT=${OMNETPP_ROOT_DEFAULT}#" \
    -e "s#^OPEN5GS_CONFIG_DIR=.*#OPEN5GS_CONFIG_DIR=${PROJECT_ROOT}/configs/core#" \
    -e "s#^OPEN5GS_SUBSCRIBERS_FILE=.*#OPEN5GS_SUBSCRIBERS_FILE=${PROJECT_ROOT}/configs/core/subscribers.yaml#" \
    -e "s#^SRSRAN_GNB_CONFIG=.*#SRSRAN_GNB_CONFIG=${PROJECT_ROOT}/configs/gnb/gnb_zmq_compat.yaml#" \
    -e "s#^SRSRAN_UE_CONFIG=.*#SRSRAN_UE_CONFIG=${PROJECT_ROOT}/configs/ue/ue_zmq_compat.conf#" \
    -e "s#^GNURADIO_CHANNEL_PROFILE=.*#GNURADIO_CHANNEL_PROFILE=${PROJECT_ROOT}/configs/channel/bypass_compat.yaml#" \
    -e "s#^NR_PROFILE=.*#NR_PROFILE=${PROJECT_ROOT}/configs/nr_profiles/bootstrap_compat_mu0_15k.yaml#" \
    -e "s#^STATE_FILE=.*#STATE_FILE=${PROJECT_ROOT}/outputs/runtime/state.json#" \
    -e "s#^STATE_ENV_FILE=.*#STATE_ENV_FILE=${PROJECT_ROOT}/outputs/runtime/omnetpp.env#" \
    -e "s#^EVENT_LOG=.*#EVENT_LOG=${PROJECT_ROOT}/outputs/runtime/events.jsonl#" \
    -e "s#^METRICS_FILE=.*#METRICS_FILE=${PROJECT_ROOT}/outputs/runtime/metrics.json#" \
    "${PROJECT_ROOT}/.env.example" > "${PROJECT_ROOT}/.env"
}

build_omnetpp_project() {
  log "Building the local OMNeT++ visualization project."
  export OMNETPP_ROOT="${OMNETPP_ROOT_DEFAULT}"
  bash "${PROJECT_ROOT}/omnetpp/build.sh"
}

run_post_install_setup() {
  log "Applying network setup and Open5GS subscriber provisioning."
  bash "${PROJECT_ROOT}/scripts/setup_host_network.sh"
  PATH="${PYTHON_VENV}/bin:${PATH}" PYTHONPATH="${PROJECT_ROOT}" \
    python3 -m tools.provision_subscribers \
    --subscribers "${PROJECT_ROOT}/configs/core/subscribers.yaml" \
    --db-uri "mongodb://127.0.0.1/open5gs"
}

start_stack_if_requested() {
  if [[ "${AUTO_START_STACK:-1}" != "1" ]]; then
    return 0
  fi
  export OMNETPP_ROOT="${OMNETPP_ROOT_DEFAULT}"
  export PATH="${PYTHON_VENV}/bin:${PATH}"
  log "Starting the SITL stack."
  bash "${PROJECT_ROOT}/scripts/start_all.sh"
  if [[ "${AUTO_RUN_HEALTHCHECK:-1}" == "1" ]]; then
    bash "${PROJECT_ROOT}/scripts/healthcheck.sh" || true
  fi
}

install_base_packages
install_open5gs
install_mongodb
install_srsran_packages
install_python_env
install_omnetpp
write_env_file
build_omnetpp_project
run_post_install_setup
start_stack_if_requested

log "Bootstrap completed."
log "Python venv: ${PYTHON_VENV}"
log "OMNeT++ root: ${OMNETPP_ROOT_DEFAULT}"
log "Project environment file: ${PROJECT_ROOT}/.env"
