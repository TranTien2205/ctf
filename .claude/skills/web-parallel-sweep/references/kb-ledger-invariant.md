# The ledger invariant

Method module for `web-parallel-sweep`. The sweep splits a web target by bug-class family into bounded measurements; this file is one named piece of that method. Ten families reporting is not ten families closed.

state.json has exactly one writer (the main thread via
hooks.py) - the whole no-Write-agents rule exists to keep
this true under parallelism.

## Pivot

Module read -> back to the sweep procedure, or the sibling module the
question names.
