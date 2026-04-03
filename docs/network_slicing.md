# Network Slicing

Slice profiles live under `configs/slicing/`.

Included profiles:

- `embb`
- `urllc`
- `mmtc`
- `custom_research`

Slice concepts represented:

- SST
- SD
- DNN mapping
- QoS profile
- subscriber/UE mapping
- traffic template
- KPI targets
- optional RAN scheduler policy hints

Current implementation model:

- profile-driven slice emulation using DNN/QoS/subscriber grouping and testcase-aware policy switching

If full dynamic slicing is unavailable in the selected stack, the profile-based model remains the default and is the expected research workflow for this scaffold.
