#!/usr/bin/env bash
set -euo pipefail

sudo iptables -P FORWARD ACCEPT
sudo iptables -C FORWARD -i ogstun -j ACCEPT 2>/dev/null || sudo iptables -A FORWARD -i ogstun -j ACCEPT
sudo iptables -C FORWARD -o ogstun -j ACCEPT 2>/dev/null || sudo iptables -A FORWARD -o ogstun -j ACCEPT
echo "Forwarding rules ready."
