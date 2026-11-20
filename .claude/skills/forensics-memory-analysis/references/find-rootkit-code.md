# rootkit signals via injected code

**Goal:** rootkit signals — plugin route `ssdt/driverirp/callbacks/unloadedmodules`.

**Artifact:** injected code — plugin route `malfind,ldrmodules,apihooks`.

Run the goal route first; the artifact route deepens a finding. Record the plugin + verbatim output row.
