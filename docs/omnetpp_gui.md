# OMNeT++ GUI

OMNeT++ provides two main views:

- `Architecture View`: fixed zoned layout of core, RAN, RF, channel, measurement, and control blocks
- `Runtime View`: live labels showing component state, active testcase, active slice, active NR profile, channel profile, attach state, UE IP, and latency KPIs

Visualized paths:

- control plane
- user plane
- ZMQ uplink/downlink sample paths
- measurement/export paths
- testcase control flow
- slice application flow

State source:

- `outputs/runtime/omnetpp.env`

Fallback source:

- `outputs/runtime/omnetpp_state.json`

Build:

1. export `OMNETPP_ROOT`
2. run `bash omnetpp/build.sh`
3. run `bash scripts/start_omnetpp_gui.sh`
