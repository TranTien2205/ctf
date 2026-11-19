# CBC IV prediction — the BEAST-shaped case — deep

When the IV for the NEXT message is predictable (chained from the previous
ciphertext block — the old TLS1.0 bug), chosen plaintext verifies guesses.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Need | Check |
|---|---|
| You see IV_next before choosing plaintext | the protocol emits it |
| You can submit chosen plaintext blocks | an encrypt oracle |
| Byte-boundary control | prefix alignment as in ECB |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
