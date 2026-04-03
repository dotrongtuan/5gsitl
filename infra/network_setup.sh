#!/usr/bin/env bash
set -euo pipefail

sudo ip tuntap add name ogstun mode tun 2>/dev/null || true
sudo ip addr add 10.45.0.1/16 dev ogstun 2>/dev/null || true
sudo ip link set ogstun up
sudo iptables -t nat -C POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE 2>/dev/null || \
  sudo iptables -t nat -A POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE
echo "Open5GS tunnel and NAT rules prepared."
