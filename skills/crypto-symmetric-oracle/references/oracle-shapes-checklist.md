# Oracle shapes — the four you can hold — operational checklist

An oracle is any endpoint that answers a question about a ciphertext, a plaintext, or a tag. Before any exploit loop, name exactly which one you hold — encrypt, decrypt, padding-check, or verify — because the attack inventory differs completely per shape.

## Checklist

- [ ] Send 32+ identical bytes; identical 16-byte ciphertext blocks confirm ECB.
- [ ] Send two different lengths; a length-preserving output marks CTR/stream, padded output marks ECB/CBC.
- [ ] Corrupt one ciphertext byte; a padding-specific error vs a generic reject separates the oracle kinds.
- [ ] Check whether a tag is verified BEFORE decryption — if yes, the class is closed for malleability attacks.

## Abort conditions

- A 500-vs-200 pair is not automatically a padding oracle: compare invalid pad vs valid pad/invalid MAC first.
- Gzip/deflate before encryption destroys byte-at-a-time alignment — the ciphertext length stops tracking input length.
- A service that rate-limits at ~10 req/s cannot sustain a 40k-request padding loop; count request budget first.

## Falsifier

Falsifier — the service authenticates before decrypting (GCM tag, or HMAC verified first). A tampered ciphertext is rejected identically for every corruption; no oracle exists to query. Reclassify toward nonce reuse or key-material leaks instead.

## Cross-references

`ecb-detection.md` · `cbc-padding-oracle.md` · `ctr-nonce-reuse.md` · `mac-forgery.md` · `../field-notes.md`
