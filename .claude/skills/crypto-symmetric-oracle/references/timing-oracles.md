# Timing oracles — when time is the only channel

When status and body are identical, timing remains. It works but it's fragile: jitter, warmup, and load can all masquerade as signal.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Identical responses, but rejects faster/slower by position | early-exit compare | position-recovery loop |
| Decryption slow path vs fast path | padding valid/invalid timing | padding oracle via time |
| Service sleeps on some conditions | explicit delay oracle | trivially measured |

## Steps

1. Measure baseline: 50+ samples of a valid request; record median + spread.
2. Test the discriminating condition with 50+ samples; a separated distribution is the oracle.
3. If distributions overlap, double the samples; if they still overlap, the timing channel is too noisy.
4. Drive the byte-recovery loop using median comparisons, not single requests.

## Falsifier

Falsifier — even with 200+ samples, the two distributions overlap completely: no timing oracle. Reclassify.

## Traps

- A 1-byte-early exit difference is ~1ns — invisible over the network; only macro differences (crypto ops, sleeps) survive.
- Load on the target destroys timing signal — measure when quiet.
- Warmup: the first request is always different — discard it.

## Commands

```bash
python3 tools/pad_oracle.py --ct <h> --url 'https://t/d?c={CT}' --ok-regex 'ok'
```

## Cross-references

`response-distinguishers.md` · `cbc-padding-oracle.md`
