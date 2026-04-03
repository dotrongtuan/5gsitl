# PHY Testcases

Implemented channel-oriented cases:

- bypass
- awgn_low
- awgn_sweep
- fading_pedestrian
- fading_stress
- delay_1ms
- delay_3ms
- jitter_stress
- freq_offset_small
- asymmetric_ul_dl
- scheduler_stress

Supported impairment knobs:

- AWGN proxy through channel noise voltage
- fading profile placeholder
- fixed delay
- jitter approximation
- frequency offset
- asymmetric UL/DL loss

For richer fading models or sample-rate mismatch emulation, extend `gnuradio/channel_emulator.py`.
