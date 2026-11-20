# Time accounting

Method module for `web-parallel-sweep`. The sweep splits a web target by bug-class family into bounded measurements; this file is one named piece of that method. Ten families reporting is not ten families closed.

The sweep's payoff is wall-clock: ten serial ~10-minute
measurements become one parallel round. The accounting counts
orchestration overhead honestly - it is not zero.

## Pivot

Module read -> back to the sweep procedure, or the sibling module the
question names.
