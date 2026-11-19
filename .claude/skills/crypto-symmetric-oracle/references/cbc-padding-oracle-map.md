# CBC padding oracle — Vaudenay decryption — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Corrupt ciphertext yields two distinct error responses | padding oracle confirmed | drive pad_oracle loop |
| Same ciphertext replayed gives same validity answer | deterministic oracle | full decryption feasible |
| All tampering returns one generic error | no oracle — authenticated or uniform error | reclassify |

## Falsifier

Falsifier — every corruption returns byte-identical responses (status, body, AND timing within noise): no oracle exists. An HMAC checked before decryption produces exactly this signature.
