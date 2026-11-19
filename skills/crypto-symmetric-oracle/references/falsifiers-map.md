# Falsifiers — the observations that close each attack — map

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

Expanded rows and abort conditions: `falsifiers.md` and `falsifiers-deep.md`.
