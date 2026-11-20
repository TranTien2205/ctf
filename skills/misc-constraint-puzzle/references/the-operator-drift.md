# New operators mid-run — dispatch table

Round N adds `*`, then `-`, then parentheses — keep the operator set
in a dispatch table so adding one is a dict entry, not a rewrite.

## Growth

The ramp adds operators — the table absorbs them.
