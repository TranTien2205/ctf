# sleep — the timing oracle


sleep(n) called via the chain pauses the process — a deliberate timing
signal when no direct output exists.

## The oracle

A chain that conditionally calls sleep leaks a bit per run: does the
response take ~n seconds? The timing is the observable.
