#!/usr/bin/env bash
set -euo pipefail

sudo sysctl -w net.core.rmem_max=33554432
sudo sysctl -w net.core.wmem_max=33554432
sudo sysctl -w net.core.netdev_max_backlog=250000
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1
echo "Host tuning applied for SITL operation."
