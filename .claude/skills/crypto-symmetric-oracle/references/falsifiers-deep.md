# Falsifiers — the observations that close each attack — deep

Every attack in this class has a specific observation that kills it. Check
the falsifier before investing a loop; the falsifier is cheaper than the
attack.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Attack | Falsifier |
|---|---|
| ECB fingerprint | no duplicated block in a 48-byte repeated input |
| Byte-at-a-time | recovered bytes stop being coherent mid-loop |
| Cut-and-paste | token carries MAC over whole ciphertext |
| CBC padding oracle | all corruptions → identical response incl. timing |
| CBC bit-flip | token authenticated, or parser rejects garbage block |
| CTR/keystream reuse | every nonce distinct across captures |
| Crib-drag | no offset yields printable on both sides under any crib |
| GCM nonce reuse | no reused nonce in captures |
| Length extension | forged MAC rejected at all secret lengths |
| Single-byte XOR | no key gives mostly-printable output |
| HMAC/verify timing | distributions overlap at 200+ samples |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
