# rootkit signals via memory content

**Goal:** rootkit signals — plugin route `ssdt/driverirp/callbacks/unloadedmodules`.

**Artifact:** memory content — plugin route `memmap,vadinfo,procdump`.

Run the goal route first; the artifact route deepens a finding. Record the plugin + verbatim output row.
