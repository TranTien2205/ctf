# Orchestration order

Method module for `web-parallel-sweep`. The sweep splits a web target by bug-class family into bounded measurements; this file is one named piece of that method. Ten families reporting is not ten families closed.

recon -> bundle (when the bundle is the source) -> the nine
read-only families in parallel -> race proposes, main thread
executes -> validate -> merge -> decide. The order is load-
bearing: downstream families need recon's inventory.

## Pivot

Module read -> back to the sweep procedure, or the sibling module the
question names.
