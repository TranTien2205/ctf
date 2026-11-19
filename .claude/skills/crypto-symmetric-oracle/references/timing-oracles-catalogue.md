# Timing oracles — when time is the only channel — case catalogue

When status and body are identical, timing remains. It works but it's fragile: jitter, warmup, and load can all masquerade as signal.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Identical responses, but rejects faster/slower by position | early-exit compare | position-recovery loop |
| 2 | Decryption slow path vs fast path | padding valid/invalid timing | padding oracle via time |
| 3 | Service sleeps on some conditions | explicit delay oracle | trivially measured |

## Falsifier

Falsifier — even with 200+ samples, the two distributions overlap completely: no timing oracle. Reclassify.

## Coverage notes

- A 1-byte-early exit difference is ~1ns — invisible over the network; only macro differences (crypto ops, sleeps) survive.
- Load on the target destroys timing signal — measure when quiet.
- Warmup: the first request is always different — discard it.

## Cross-references

`response-distinguishers.md` · `cbc-padding-oracle.md`
