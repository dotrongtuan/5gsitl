#!/usr/bin/env bash
set -euo pipefail

sudo ip link add sitl_n2 type dummy 2>/dev/null || true
sudo ip link add sitl_n3 type dummy 2>/dev/null || true
sudo ip addr add 10.10.0.10/24 dev sitl_n2 2>/dev/null || true
sudo ip addr add 10.10.0.2/24 dev sitl_n2 2>/dev/null || true
sudo ip addr add 10.20.0.1/24 dev sitl_n3 2>/dev/null || true
sudo ip addr add 10.20.0.2/24 dev sitl_n3 2>/dev/null || true
sudo ip link set sitl_n2 up
sudo ip link set sitl_n3 up

sudo ip tuntap add name ogstun mode tun 2>/dev/null || true
sudo ip addr add 10.45.0.1/16 dev ogstun 2>/dev/null || true
sudo ip link set ogstun up
sudo iptables -t nat -C POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE 2>/dev/null || \
  sudo iptables -t nat -A POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE
echo "Open5GS tunnel, dummy N2/N3 interfaces, and NAT rules prepared."
