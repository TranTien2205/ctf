# Detection — naming the oracle in ≤5 requests — checklist

The discriminator runs once, before any exploit. Five probes, each cheap,
each ruling out a branch.

## Checklist

- [ ] **Replay** — same input twice. Identical output → deterministic (ECB or

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
