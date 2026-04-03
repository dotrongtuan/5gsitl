# SITL Design

Design principle:

- every major component runs in software on Ubuntu
- connectivity is achieved with host processes, namespaces, tunnels, ZMQ, and software bridges
- reproducibility is preferred over hardware fidelity

Primary adapter:

- file-based polling from `outputs/runtime/state.json`, `metrics.json`, and `omnetpp.env`

Fallback adapter:

- local REST polling via `tools/event_bus.py`

Why file polling is primary:

- robust across versions
- easy to debug
- compatible with OMNeT++ polling without extra plugins

Version-sensitive items:

- Open5GS daemon config keys
- srsRAN gNB/srsUE config schemas
- GNU Radio ZMQ block signatures
- OMNeT++ build/library path behavior

All of these are marked `TODO(version-check)` where they matter.
