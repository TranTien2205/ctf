# rootkit signals via strings

**Goal:** rootkit signals — plugin route `ssdt/driverirp/callbacks/unloadedmodules`.

**Artifact:** strings — plugin route `ioc_scan,strings --utf16`.

Run the goal route first; the artifact route deepens a finding. Record the plugin + verbatim output row.
