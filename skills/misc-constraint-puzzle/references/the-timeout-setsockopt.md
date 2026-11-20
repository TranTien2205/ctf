# Socket timeouts — two clocks

`s.settimeout(t)` bounds each recv; the round deadline is the
server's — keep recv timeouts a little under it so the solver
reports the drop rather than hanging.

## settimeout

Bounds the recv; the round deadline bounds the solve.
