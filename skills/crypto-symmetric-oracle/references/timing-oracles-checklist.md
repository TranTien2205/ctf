# Timing oracles — when time is the only channel — operational checklist

When status and body are identical, timing remains. It works but it's fragile: jitter, warmup, and load can all masquerade as signal.

## Checklist

- [ ] Measure baseline: 50+ samples of a valid request; record median + spread.
- [ ] Test the discriminating condition with 50+ samples; a separated distribution is the oracle.
- [ ] If distributions overlap, double the samples; if they still overlap, the timing channel is too noisy.
- [ ] Drive the byte-recovery loop using median comparisons, not single requests.

## Abort conditions

- A 1-byte-early exit difference is ~1ns — invisible over the network; only macro differences (crypto ops, sleeps) survive.
- Load on the target destroys timing signal — measure when quiet.
- Warmup: the first request is always different — discard it.

## Falsifier

Falsifier — even with 200+ samples, the two distributions overlap completely: no timing oracle. Reclassify.

## Cross-references

`response-distinguishers.md` · `cbc-padding-oracle.md`
