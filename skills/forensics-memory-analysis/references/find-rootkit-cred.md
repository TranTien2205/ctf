# rootkit signals via credentials

**Goal:** rootkit signals — plugin route `ssdt/driverirp/callbacks/unloadedmodules`.

**Artifact:** credentials — plugin route `hashdump,lsadump,cachedump`.

Run the goal route first; the artifact route deepens a finding. Record the plugin + verbatim output row.
