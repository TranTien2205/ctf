# rootkit signals via network state

**Goal:** rootkit signals — plugin route `ssdt/driverirp/callbacks/unloadedmodules`.

**Artifact:** network state — plugin route `netscan,connscan`.

Run the goal route first; the artifact route deepens a finding. Record the plugin + verbatim output row.
