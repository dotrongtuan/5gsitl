# OMNeT++ Project Notes

This OMNeT++ project is the visualization and experiment front-end for the SITL runtime.

- `ned/` contains the research topology and visual zones.
- `src/` contains the polling bridge that reads `outputs/runtime/omnetpp.env`.
- `simulations/omnetpp.ini` configures the runtime view.
- `build.sh` compiles the shared library for `opp_run`.

Primary runtime feed:

- `outputs/runtime/omnetpp.env`

Fallback runtime feed:

- `outputs/runtime/omnetpp_state.json`

`TODO(version-check)` markers exist where OMNeT++ 6.x build or display-string behavior may vary.
