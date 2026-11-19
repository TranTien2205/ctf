# Error timing — the hidden distinguisher — deep

When two error types produce identical text, timing still separates them: a crypto-check error is slower than a parse error.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — indistinguishable distributions at 200+ samples: no timing signal.

## Highest-cost traps

- Timing is the last resort — always prefer content/status distinguishers.
- Warmup and jitter correction are mandatory.
- This boundary overlaps web-xs-leaks.

## Commands

```bash
for i in $(seq 50); do curl -s -o /dev/null -w '%{time_total}\n' '$BASE/bad1'; done
```

## Cross-references

`response-anatomy.md` · `evidence.md`
