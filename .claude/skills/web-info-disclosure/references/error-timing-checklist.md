# Error timing — the hidden distinguisher — checklist

When two error types produce identical text, timing still separates them: a crypto-check error is slower than a parse error.

## Checklist

- [ ] Baseline the two error types with 50+ samples each.
- [ ] Compare medians — a separated distribution is a signal.
- [ ] Cache timing reveals whether a resource was fetched before (xs-leaks adjacent).
- [ ] If distributions overlap at 200 samples, the channel is dead.

## Abort conditions

- Timing is the last resort — always prefer content/status distinguishers.
- Warmup and jitter correction are mandatory.
- This boundary overlaps web-xs-leaks.

## Falsifier

Falsifier — indistinguishable distributions at 200+ samples: no timing signal.
