# rootkit signals via file objects

**Goal:** rootkit signals — plugin route `ssdt/driverirp/callbacks/unloadedmodules`.

**Artifact:** file objects — plugin route `filescan,dumpfiles,mftscan`.

Run the goal route first; the artifact route deepens a finding. Record the plugin + verbatim output row.
