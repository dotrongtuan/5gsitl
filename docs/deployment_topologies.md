# Deployment Topologies

## Single Host

- one Ubuntu host
- Open5GS, gNB, UE, GNU Radio, adapters, OMNeT++, and captures all local
- best for lab bring-up and demos

## Split Host

- host A: 5GC
- host B: gNB + GNU Radio + OMNeT++ GUI
- host C: UE

Recommended use:

- larger experiments where CPU isolation matters
- clean control/user-plane capture separation

## Multi-VM / Container Lab

- one VM/container per functional block
- management scripts still run from the project root
- adapters aggregate remote logs/state into the OMNeT++ layer

All addresses, ports, tunnels, and endpoints remain configurable through `.env` and `configs/`.
