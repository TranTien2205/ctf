# POODLE and the legacy TLS padding family — deep

POODLE is the CBC padding oracle against SSL 3.0 / TLS CBC ciphersuites.
The same shape appears in CTF services that expose a TLS-like decrypt.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Variant | Pad semantics | Oracle answer |
|---|---|---|
| PKCS#7 (app-layer) | last N bytes = N | strict — full Vaudenay |
| SSL3 POODLE | last byte = pad len only | weaker — needs block shifting |
| TLS1.0 explicit IV | first block is IV | treat IV as C_{i-1} |
| Lucky13 timing | pad check timing differs | timing-channel variant |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
