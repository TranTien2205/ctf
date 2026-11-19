# Symmetric-oracle workflow — the ordered path — deep

The class is defined by one question: which oracle do you hold? Everything
else is mechanical once that is named.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Observation | Oracle | Next file |
|---|---|---|
| Identical blocks for identical input | ECB encrypt | `ecb-detection.md` |
| Pad-corrupt vs MAC-corrupt differ | CBC padding oracle | `cbc-padding-oracle.md` |
| Two ciphertexts, same nonce | stream/CTR reuse | `ctr-nonce-reuse.md` |
| `hash(secret||m)` construction | prefix MAC | `length-extension.md` |
| Tag checked before decrypt | authenticated | `authenticated-boundary.md` |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
