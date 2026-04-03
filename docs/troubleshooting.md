# Troubleshooting

## Core Does Not Start

- verify MongoDB is reachable
- if you used the one-click bootstrap, confirm `systemctl status mongod` is healthy
- inspect `outputs/logs/open5gs/*.stdout.log`
- compare daemon config keys with installed package version

## gNB or UE Fails

- confirm `gnb` and `srsue` binaries are installed
- confirm the compatibility defaults in `.env` point to `gnb_zmq_compat.yaml` and `ue_zmq_compat.conf`
- confirm the current attach baseline in `docs/runtime_compat_attach_baseline.md`
- verify ZMQ endpoints in `configs/zmq/links.yaml`
- confirm the UE namespace exists
- on Ubuntu `24.04`, if Launchpad PPA installation fails, rerun the patched bootstrap so it uses source builds for `srsRAN Project` and `srsRAN 4G`

## Channel Emulator Is Idle

- inspect `outputs/runtime/channel_status.json`
- for the compatibility attach path, `bypass_compat.yaml` should report `direct-zmq`
- if GNU Radio blocks fail to load, the runner falls back to dummy mode
- regenerate the `.grc` locally if needed

## Registration Reaches NAS But Attach Still Fails

- inspect `outputs/logs/open5gs/amf.log`, `outputs/logs/open5gs/pcf.stdout.log`, `outputs/logs/open5gs/udm.stdout.log`, and `outputs/logs/open5gs/udr.stdout.log`
- if AMF reports `No [npcf-am-policy-control]`, make sure `OPEN5GS_ENABLE_PCF=1`
- if PCF reports a MongoDB collection error, make sure `configs/core/pcf.yaml` includes `db_uri: mongodb://127.0.0.1/open5gs`
- verify `configs/core/subscribers_compat.yaml` is the active subscriber source and contains IMSI `001010123456780`

## OMNeT++ Labels Do Not Update

- check `outputs/runtime/omnetpp.env`
- ensure the adapter processes are running
- rebuild the OMNeT++ library after source changes
- if `./configure` fails on OpenSceneGraph, install `libopenscenegraph-dev` and rerun the bootstrap or `./configure`
