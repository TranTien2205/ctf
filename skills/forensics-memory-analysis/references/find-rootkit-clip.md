# rootkit signals via clipboard/console

**Goal:** rootkit signals — plugin route `ssdt/driverirp/callbacks/unloadedmodules`.

**Artifact:** clipboard/console — plugin route `clipboard,consoles,cmdscan`.

Run the goal route first; the artifact route deepens a finding. Record the plugin + verbatim output row.
