# 5g-nr-sitl-omnetpp-testbed

`5g-nr-sitl-omnetpp-testbed` is a software-only 5G NR SA research testbed for repeatable system-level experimentation on Ubuntu Linux. It treats URLLC as one supported scenario class inside a broader 5G NR platform that also covers baseline SA connectivity, eMBB, mMTC-like workloads, PHY/channel studies, slice-aware experiments, packet capture analysis, and OMNeT++-driven visualization.

## Project Objective

The project provides a practical SITL harness where:

- the 5G Core runs as host processes or containers,
- the virtual RAN runs as software gNB and software UE processes,
- virtual RF uses ZeroMQ sample streams,
- GNU Radio emulates channel impairments in software,
- OMNeT++ acts as the architecture GUI, runtime dashboard, experiment monitor, and scenario front-end,
- Python and Bash handle orchestration, adapters, reporting, and reproducibility.

No SDR, USRP, OTA, or physical RF front-end is required.

## Full 5G NR Scope

Supported experiment categories:

- 5G NR SA attach, PDU session establishment, and baseline connectivity
- URLLC-style low-latency tests
- eMBB sustained throughput and tradeoff studies
- mMTC-like burst/small payload behavior
- channel impairment and PHY sensitivity studies
- slice-aware traffic and KPI experiments
- packet capture, Wireshark, and report generation
- OMNeT++ topology visualization and runtime overlay monitoring

## Architecture Overview

The testbed is split into six explicit zones mirrored in the OMNeT++ topology:

1. `5G Core zone`: AMF, SMF, UPF, UDM, NRF, AUSF, optional PCF, optional NSSF
2. `Virtual RAN zone`: software gNB and software UE
3. `Virtual RF zone`: ZeroMQ uplink and downlink sample paths
4. `Channel Simulation zone`: GNU Radio channel emulator for bypass, AWGN, fading, delay, jitter proxy, frequency offset, asymmetric UL/DL, and burst loss
5. `Measurement / Observability zone`: latency monitor, KPI collector, packet capture, metrics export, logs
6. `Scenario / Slicing / Experiment Control zone`: testcase runner, slice profile selector, use-case manager, report generator

## OMNeT++ GUI Overview

OMNeT++ is the main visualization layer. It shows:

- static architecture zoning
- runtime component state
- control-plane and user-plane paths
- ZMQ UL/DL sample paths
- capture points
- testcase control flow
- slice profile application flow
- current RTT, p95, p99, loss, jitter, scenario, testcase, slice, attach state, and UE IP

Runtime data is fed into OMNeT++ by the adapter layer.

Primary adapter approach:

- `file-based polling` from `outputs/runtime/*.json` and `outputs/runtime/omnetpp.env`

Fallback adapter approach:

- `local REST polling` from the lightweight Python event bus

Version-sensitive glue points are marked `TODO(version-check)`.

## Runtime Assumptions

This scaffold is optimized around:

- Ubuntu `22.04` or `24.04`
- host-installed `Open5GS`
- host-installed `srsRAN Project` gNB with ZeroMQ support
- host-installed `srsRAN 4G` `srsUE` for software UE lab use
- host-installed `GNU Radio`
- OMNeT++ `6.x` with a local build of this project

## Quick Start

One-command bootstrap on Ubuntu:

```bash
bash scripts/bootstrap_ubuntu_sitl.sh
```

The bootstrap script installs the required Ubuntu packages, MongoDB, Open5GS, srsRAN Project, srsRAN 4G, OMNeT++, Python dependencies, generates `.env`, provisions subscribers, builds the OMNeT++ project, and by default starts the baseline SITL stack.

Compatibility note:

- the bootstrap defaults to a `15 kHz SCS` compatibility profile for `srsUE`-based SA proof-of-concept bring-up
- the original research-oriented `mu=1 / 30 kHz` profiles are still preserved under `configs/nr_profiles/`
- on Ubuntu `24.04`, the bootstrap falls back to source builds for `srsRAN Project` and `srsRAN 4G` because Launchpad PPA coverage may be incomplete
- the bootstrap installs `libopenscenegraph-dev` and keeps OMNeT++ OpenSceneGraph support enabled by default; set `OMNETPP_ENABLE_OSG=0` only if you explicitly want a minimal build

1. Copy `.env.example` to `.env` and adjust paths for `Open5GS`, `srsRAN`, `GNU Radio`, and `OMNeT++`.
2. Run `scripts/install_dependencies.sh`.
3. Run `scripts/setup_host_network.sh`.
4. Run `scripts/start_core.sh`.
5. Run `scripts/start_gnb.sh`.
6. Run `scripts/start_ue.sh`.
7. Run `scripts/start_channel.sh`.
8. Run `scripts/start_adapters.sh`.
9. Run `scripts/start_omnetpp_gui.sh`.
10. Run `scripts/run_testcase.sh testcases/nr/nr_baseline_connectivity.yaml`.

## Demo In 10 Steps

1. `cp .env.example .env`
2. `vim .env`
3. `bash scripts/install_dependencies.sh`
4. `bash scripts/setup_host_network.sh`
5. `bash scripts/start_all.sh`
6. `bash scripts/healthcheck.sh`
7. `bash scripts/run_ping_test.sh`
8. `bash scripts/start_capture.sh baseline`
9. `bash scripts/run_testcase.sh testcases/latency/baseline_rtt.yaml`
10. `bash scripts/export_results.sh`

## One-Command Runtime Demo

To start the stack, open OMNeT++ directly in `RuntimeView`, and run the baseline latency testcase in one shot:

```bash
bash scripts/run_runtime_demo.sh
```

To run a different testcase with the same flow:

```bash
bash scripts/run_runtime_demo.sh testcases/nr/nr_baseline_connectivity.yaml
```

The runtime demo now waits for actual UE attach evidence before running the testcase. If UE attach or routing is incomplete, the demo exits with a failure instead of silently producing synthetic-looking baseline results.

## Running Captures

- all-in-one capture: `bash scripts/start_capture.sh testcase-name`
- N2-specific: `bash scripts/capture_n2.sh testcase-name`
- N3-specific: `bash scripts/capture_n3.sh testcase-name`
- UPF/downlink host path: `bash scripts/capture_upf_dn.sh testcase-name`
- bridge capture: `bash scripts/capture_host_bridge.sh testcase-name`
- stop: `bash scripts/stop_capture.sh`

Outputs land in `outputs/pcap/`.

## Running NR Experiments

- direct profile run: `bash scripts/run_nr_experiment.sh configs/nr_profiles/default_mu1_30k.yaml`
- testcase-based run: `bash scripts/run_testcase.sh testcases/nr/nr_sa_attach.yaml`
- suite run: `python3 tools/run_suite.py testcases/nr`

## Running PHY / Channel Experiments

- bypass: `bash scripts/start_channel.sh configs/channel/bypass.yaml`
- AWGN: `bash scripts/start_channel.sh configs/channel/awgn.yaml`
- fading stress: `bash scripts/run_testcase.sh testcases/phy/fading_stress.yaml`
- asymmetry: `bash scripts/run_testcase.sh testcases/phy/asymmetric_ul_dl.yaml`

## Applying Slice Profiles

- validate: `python3 tools/validate_slice_config.py configs/slicing/urllc.yaml`
- apply: `python3 tools/apply_slice_profile.py configs/slicing/urllc.yaml`
- combined run: `bash scripts/run_slice_usecase.sh configs/slicing/embb.yaml testcases/slicing/embb_stream.yaml`

## Troubleshooting Pointers

- confirm `mongod`, `open5gs-*`, `gnb`, `srsue`, `python3`, `gnuradio-companion`, `opp_run` are installed
- check `outputs/logs/` before chasing OMNeT++ display issues
- verify ZMQ port pairs in `configs/zmq/links.yaml`
- verify UE namespace and TUN setup in `scripts/setup_host_network.sh`
- compare active slice profile and testcase expectations in `outputs/runtime/state.json`
- use `scripts/healthcheck.sh` and `python3 tools/session_checker.py`
- if one-click bootstrap was used, inspect `scripts/bootstrap_ubuntu_sitl.sh` output plus `outputs/logs/open5gs/` first

## Known Limitations

- real PHY fidelity is bounded by the software-only ZMQ/GNU Radio chain
- HARQ and retransmission behavior are only partially emulated at the system level
- `srsUE`-based lab workflows are version-sensitive and bandwidth-limited compared with full commercial UE simulators
- Open5GS config shape and srsRAN config keys can vary between versions and may require `TODO(version-check)` updates
- OMNeT++ is used as visualization/orchestration, not as the primary packet-forwarding engine

## Final Notes

The scaffold is intentionally practical: it prioritizes a reproducible lab workflow over idealized full-stack perfection. The supplied scripts, adapters, configs, testcases, docs, and OMNeT++ project are designed to be extended as stack versions and research needs evolve.
