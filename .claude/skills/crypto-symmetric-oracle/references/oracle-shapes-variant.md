# Oracle shapes — the four you can hold — surface variants

An oracle is any endpoint that answers a question about a ciphertext, a plaintext, or a tag. Before any exploit loop, name exactly which one you hold — encrypt, decrypt, padding-check, or verify — because the attack inventory differs completely per shape.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| You submit bytes, service returns ciphertext | encrypt oracle (ECB/CBC/CTR under a hidden key) | alignment and mode fingerprinting first |
| Service decrypts and returns plaintext or a decode error | full decrypt oracle | usually trivial — request the flag's decryption |
| Service decrypts and only reports validity | padding/validity oracle | padding-oracle decryption loop |
| Service checks a tag you submit | verify oracle | tag-forgery or length-extension test |

## Variant-specific traps

- A 500-vs-200 pair is not automatically a padding oracle: compare invalid pad vs valid pad/invalid MAC first.
- Gzip/deflate before encryption destroys byte-at-a-time alignment — the ciphertext length stops tracking input length.
- A service that rate-limits at ~10 req/s cannot sustain a 40k-request padding loop; count request budget first.
- Base64 decoders that reject bad padding echo a DIFFERENT error than the crypto layer — read which layer answered.

## Falsifier

Falsifier — the service authenticates before decrypting (GCM tag, or HMAC verified first). A tampered ciphertext is rejected identically for every corruption; no oracle exists to query. Reclassify toward nonce reuse or key-material leaks instead.

## Cross-references

`ecb-detection.md` · `cbc-padding-oracle.md` · `ctr-nonce-reuse.md` · `mac-forgery.md` · `../field-notes.md`
