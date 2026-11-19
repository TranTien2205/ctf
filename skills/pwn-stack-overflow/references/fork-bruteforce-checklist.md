# Fork-server canary brute-force — checklist

A forking service (per-connection fork) reuses ONE canary across connections — brute it byte-by-byte through the crash-or-not signal.

## Checklist

- [ ] Confirm forking: connect twice, the canary-shaped word in a leaked stack dump matches.
- [ ] For byte i: send pad + i correct bytes + candidate; a crash = wrong byte, a clean response = right.
- [ ] Brute bytes 1-8 in order (little-endian — the low bytes first).
- [ ] Once the canary is known, the smash proceeds normally.

## Abort conditions

- Worst case 8 × 256 = 2048 connections — feasible.
- Correct byte keeps the process alive; wrong byte trips __stack_chk_fail.
- The oracle is 'did it crash', a clean binary answer.

## Falsifier

Falsifier — the server execs per connection (new canary each time) or doesn't fork: each connection has a different canary; no stable oracle.
