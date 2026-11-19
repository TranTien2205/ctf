# The null-pointer write — writing at 0


A corruption that writes near address 0: usually crashes — but an
intentional write to a mapped low page (rare) or the deliberate-crash
is sometimes the signal.

## Mostly a falsifier

A write to 0 crashes the service — it confirms the write fired but
usually isn't useful. If the page IS mapped (exotic setups), it can be
a target.
