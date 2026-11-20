# Merge is serial

Method module for `web-parallel-sweep`. The sweep splits a web target by bug-class family into bounded measurements; this file is one named piece of that method. Ten families reporting is not ten families closed.

Validation and merge happen on the main thread, one report at
a time - the ledger is a serial resource and the merge is its
only writer.

## Pivot

Module read -> back to the sweep procedure, or the sibling module the
question names.
