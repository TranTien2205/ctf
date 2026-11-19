# Preconditions — check before each attack — checklist

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

## Checklist

- [ ] check: ECB attacks
- [ ] check: Byte-at-a-time
- [ ] check: Cut-and-paste
- [ ] check: Padding oracle
- [ ] check: Bit-flip
- [ ] check: IV=key
- [ ] check: CTR reuse
- [ ] check: GCM forbidden
- [ ] check: Length ext.
- [ ] check: Single-byte XOR
- [ ] check: Crib-drag
- [ ] check: Tag truncation
- [ ] check: Timing oracle

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
