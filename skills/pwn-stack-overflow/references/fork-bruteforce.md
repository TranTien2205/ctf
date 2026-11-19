# Fork-server canary brute-force

A forking service (per-connection fork) reuses ONE canary across connections — brute it byte-by-byte through the crash-or-not signal.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| server forks per connection | canary stable across conns | byte brute |
| crash vs no-crash signal | canary byte oracle | 256 × 8 worst |

## Steps

1. Confirm forking: connect twice, the canary-shaped word in a leaked stack dump matches.
2. For byte i: send pad + i correct bytes + candidate; a crash = wrong byte, a clean response = right.
3. Brute bytes 1-8 in order (little-endian — the low bytes first).
4. Once the canary is known, the smash proceeds normally.

## Falsifier

Falsifier — the server execs per connection (new canary each time) or doesn't fork: each connection has a different canary; no stable oracle.

## Traps

- Worst case 8 × 256 = 2048 connections — feasible.
- Correct byte keeps the process alive; wrong byte trips __stack_chk_fail.
- The oracle is 'did it crash', a clean binary answer.

## Cross-references

`canary-bypass.md` · `remote-vs-local.md`
