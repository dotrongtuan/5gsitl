# Troubleshooting

## Core Does Not Start

- verify MongoDB is reachable
- if you used the one-click bootstrap, confirm `systemctl status mongod` is healthy
- inspect `outputs/logs/open5gs/*.stdout.log`
- compare daemon config keys with installed package version

## gNB or UE Fails

- confirm `gnb` and `srsue` binaries are installed
- confirm the compatibility defaults in `.env` point to `gnb_zmq_compat.yaml` and `ue_zmq_compat.conf`
- verify ZMQ endpoints in `configs/zmq/links.yaml`
- confirm the UE namespace exists
- on Ubuntu `24.04`, if Launchpad PPA installation fails, rerun the patched bootstrap so it uses source builds for `srsRAN Project` and `srsRAN 4G`

## Channel Emulator Is Idle

- inspect `outputs/runtime/channel_status.json`
- if GNU Radio blocks fail to load, the runner falls back to dummy mode
- regenerate the `.grc` locally if needed

## OMNeT++ Labels Do Not Update

- check `outputs/runtime/omnetpp.env`
- ensure the adapter processes are running
- rebuild the OMNeT++ library after source changes
- if `./configure` fails on OpenSceneGraph, install `libopenscenegraph-dev` and rerun the bootstrap or `./configure`
