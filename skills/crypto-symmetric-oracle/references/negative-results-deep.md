# Negative results — what to record when the answer is no — deep

A negative is a measurement with a falsifier attached. Recording it stops
the next pass (or the next agent) from re-proving it.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Tested | Negative observation | Reopens if |
|---|---|---|
| ECB | no duplicate block in 'A'*48 | a different injection point exists |
| Padding oracle | identical reject for every corruption | a second endpoint decrypts |
| Nonce reuse | all captured nonces distinct | more captures become available |
| Length extension | forge rejected at secret-len 8..64 | construction shown to be raw-hash |
| Bit-flip | parser rejects all garbage blocks | a don't-care field is found |
| Timing oracle | distributions overlap at 200 samples | the service gets quieter |
| Key path | no key/seed material in handout | new source surfaces |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
