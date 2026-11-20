# rootkit signals via drivers/kernel

**Goal:** rootkit signals — plugin route `ssdt/driverirp/callbacks/unloadedmodules`.

**Artifact:** drivers/kernel — plugin route `modscan,driverirp,devicetree,ssdt`.

Run the goal route first; the artifact route deepens a finding. Record the plugin + verbatim output row.
