# Evidence discipline for oracle challenges — deep

The oracle is a claim about a response channel. Evidence = the two responses
that differ, quoted verbatim.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Stage | Evidence | post-probe kind |
|---|---|---|
| ECB fingerprint | two identical ciphertext blocks from repeated input | class |
| Padding-vs-MAC split | both responses verbatim | class |
| Nonce reuse | the two captured records with the same nonce | class |
| Forged tag accepted | the verify response | impact |
| Flag in response | the live response bytes | flag via pre-flag |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
