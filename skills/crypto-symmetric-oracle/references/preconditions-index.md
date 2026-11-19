# Preconditions — check before each attack — index

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

## Companions

- `preconditions-deep.md` — boundary conditions and the failure shape
- `preconditions-checklist.md` — the same content as an ordered checklist
- `preconditions-map.md` — the lookup table alone
- `../field-notes.md` — where outcomes land
