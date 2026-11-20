# Beat the deadline — order of work

Correct first, then fast: timeouts, recv buffering, round-trip
batching only after one full round works. A fast wrong solver still
fails.

## Two clocks

recv timeout < round deadline — a stall is an error, not a hang.

## Two clocks

recv timeout < round deadline — a stall is an error, not a hang.
