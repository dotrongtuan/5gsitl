# NR Experiments

Default NR profile:

- SA mode
- `mu = 1`
- `SCS = 30 kHz`
- `slot = 0.5 ms`

Alternative profiles:

- `low_latency_mu1`
- `embb_wideband`
- `mmtc_dense`

Research directions supported by the scaffold:

- RTT studies vs channel impairment
- throughput/latency tradeoffs
- slice-aware profile comparison
- scheduler stress and policy comparison
- multi-profile regression runs

Apply a profile directly with:

- `bash scripts/run_nr_experiment.sh configs/nr_profiles/default_mu1_30k.yaml`
