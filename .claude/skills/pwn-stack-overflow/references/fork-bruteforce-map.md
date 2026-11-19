# Fork-server canary brute-force — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| server forks per connection | canary stable across conns | byte brute |
| crash vs no-crash signal | canary byte oracle | 256 × 8 worst |

## Falsifier

Falsifier — the server execs per connection (new canary each time) or doesn't fork: each connection has a different canary; no stable oracle.
