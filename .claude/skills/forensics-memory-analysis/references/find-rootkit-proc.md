# rootkit signals via process evidence

**Goal:** rootkit signals — plugin route `ssdt/driverirp/callbacks/unloadedmodules`.

**Artifact:** process evidence — plugin route `pslist,psscan,pstree`.

Run the goal route first; the artifact route deepens a finding. Record the plugin + verbatim output row.
