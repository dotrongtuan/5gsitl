# Runtime Compat Attach Baseline

This is the minimum known-good runtime configuration for software-only SA attach with `srsUE` on the current compatibility path.

## Core

- `configs/core/amf_compat.yaml`
- `configs/core/smf_compat.yaml`
- `configs/core/pcf.yaml`
- `configs/core/udm.yaml`
- `configs/core/udr.yaml`
- `configs/core/upf.yaml`
- `configs/core/subscribers_compat.yaml`

Required Open5GS settings:

- `OPEN5GS_AMF_CONFIG=$PWD/configs/core/amf_compat.yaml`
- `OPEN5GS_SMF_CONFIG=$PWD/configs/core/smf_compat.yaml`
- `OPEN5GS_SUBSCRIBERS_FILE=$PWD/configs/core/subscribers_compat.yaml`
- `OPEN5GS_ENABLE_PCF=1`
- `OPEN5GS_ENABLE_NSSF=0`
- `MONGODB_URI=mongodb://127.0.0.1/open5gs`

Important notes:

- PCF must be enabled for this Open5GS `v2.7.7` registration path.
- `configs/core/pcf.yaml` must include `db_uri: mongodb://127.0.0.1/open5gs`.
- `scripts/start_core.sh` now clears old Open5GS logs before each run and fails fast if compatibility subscriber provisioning fails.

## RAN And RF

- `configs/gnb/gnb_zmq_compat.yaml`
- `configs/ue/ue_zmq_compat.conf`
- `configs/channel/bypass_compat.yaml`

Required runtime characteristics:

- gNB and UE use direct ZMQ pairing on `127.0.0.1:2000/2001`
- channel status should report `direct-zmq`
- UE attach check should return an address from `10.45.0.0/16`

The current attach baseline is:

- band `n3`
- `15 kHz` SCS
- `20 MHz` channel bandwidth
- single slice `sst=1`, `sd=000001`
- DNN/APN `internet`
- UE namespace `ue1`

## Expected Validation Signals

- `bash scripts/check_attach.sh` returns `{"attached": true, "ue_ip": "10.45.0.x"}`
- `outputs/runtime/channel_status.json` shows `"mode": "direct-zmq"`
- `outputs/logs/open5gs/pcf.stdout.log` shows MongoDB initialization and no collection-null errors
- `outputs/logs/open5gs/amf.log` contains `Registration request` without `Registration reject`

## One-Command Run

```bash
bash scripts/run_runtime_demo.sh
```

For a clean attach-only verification:

```bash
bash scripts/check_attach.sh
cat outputs/runtime/channel_status.json
tail -n 80 outputs/logs/open5gs/amf.stdout.log
tail -n 80 outputs/logs/open5gs/pcf.stdout.log
```
