#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

sudo apt-get update
sudo apt-get install -y \
  build-essential cmake git pkg-config python3 python3-pip python3-venv \
  tcpdump tshark wireshark iproute2 iptables iperf3 jq net-tools curl \
  libzmq3-dev libczmq-dev gnuradio open5gs mongodb-clients

python3 -m pip install --user -r "${PROJECT_ROOT}/requirements.txt"

log "Dependencies installed. OMNeT++ and srsRAN builds may still require manual installation."
