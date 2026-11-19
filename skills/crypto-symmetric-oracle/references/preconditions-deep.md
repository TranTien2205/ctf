# Preconditions — check before each attack — deep

| Attack | Must be true | Check |
|---|---|---|
| ECB attacks | deterministic output for same input | replay twice |
| Byte-at-a-time | input lands before the secret | marker position probe |
| Cut-and-paste | token is block-structured, no MAC | field-mapping + tamper test |
| Padding oracle | pad vs MAC answers differ | two corruptions |
| Bit-flip | unauthenticated CBC, parser survives | tamper + parse test |
| IV=key | decrypt error echoes plaintext | the 3-block probe |
| CTR reuse | a nonce repeats | capture diff |
| GCM forbidden | same nonce + two tagged records | capture diff |
| Length ext. | raw MD hash, secret\|\|msg | source or forge probe |
| Single-byte XOR | short ct, key space = 256 | score sanity |
| Crib-drag | P1 XOR P2 + a known word | the XOR is structured |
| Tag truncation | shortened tag accepted | prefix probe |
| Timing oracle | per-position split exists | 50-sample measure |

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Attack | Must be true | Check |
|---|---|---|
| ECB attacks | deterministic output for same input | replay twice |
| Byte-at-a-time | input lands before the secret | marker position probe |
| Cut-and-paste | token is block-structured, no MAC | field-mapping + tamper test |
| Padding oracle | pad vs MAC answers differ | two corruptions |
| Bit-flip | unauthenticated CBC, parser survives | tamper + parse test |
| IV=key | decrypt error echoes plaintext | the 3-block probe |
| CTR reuse | a nonce repeats | capture diff |
| GCM forbidden | same nonce + two tagged records | capture diff |
| Length ext. | raw MD hash, secret\|\|msg | source or forge probe |
| Single-byte XOR | short ct, key space = 256 | score sanity |
| Crib-drag | P1 XOR P2 + a known word | the XOR is structured |
| Tag truncation | shortened tag accepted | prefix probe |
| Timing oracle | per-position split exists | 50-sample measure |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
