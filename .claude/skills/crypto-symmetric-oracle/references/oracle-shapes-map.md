# Oracle shapes — the four you can hold — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| You submit bytes, service returns ciphertext | encrypt oracle (ECB/CBC/CTR under a hidden key) | alignment and mode fingerprinting first |
| Service decrypts and returns plaintext or a decode error | full decrypt oracle | usually trivial — request the flag's decryption |
| Service decrypts and only reports validity | padding/validity oracle | padding-oracle decryption loop |
| Service checks a tag you submit | verify oracle | tag-forgery or length-extension test |
| You see ciphertext AND a tag AND a nonce | authenticated bundle | nonce reuse or tag-truncation, not padding |

## Falsifier

Falsifier — the service authenticates before decrypting (GCM tag, or HMAC verified first). A tampered ciphertext is rejected identically for every corruption; no oracle exists to query. Reclassify toward nonce reuse or key-material leaks instead.
