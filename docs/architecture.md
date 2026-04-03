# Architecture

The testbed is a software-only 5G NR SA system centered on six zones:

1. `5G Core`: Open5GS daemons for AMF, SMF, UPF, UDM, NRF, AUSF, optional PCF, optional NSSF
2. `Virtual RAN`: software gNB and software UE
3. `Virtual RF`: ZeroMQ sample transport
4. `Channel Simulation`: GNU Radio impairment emulator
5. `Measurement / Observability`: metrics, logs, packet capture, reporting
6. `Scenario / Slicing / Control`: testcase engine, slice selector, use-case manager, report generation

Control-plane path:

- UE/gNB registration -> AMF -> SMF -> policy/slice services

User-plane path:

- UE -> gNB -> UPF -> data network / TUN bridge

Virtual RF path:

- gNB ZMQ DL -> GNU Radio -> UE
- UE ZMQ UL -> GNU Radio -> gNB

OMNeT++ is not the packet-forwarding engine. It is the GUI/orchestration/visualization layer driven by the adapter-exported runtime state.
