# Fork-server canary brute-force — case catalogue

A forking service (per-connection fork) reuses ONE canary across connections — brute it byte-by-byte through the crash-or-not signal.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | server forks per connection | canary stable across conns | byte brute |
| 2 | crash vs no-crash signal | canary byte oracle | 256 × 8 worst |

## Falsifier

Falsifier — the server execs per connection (new canary each time) or doesn't fork: each connection has a different canary; no stable oracle.
