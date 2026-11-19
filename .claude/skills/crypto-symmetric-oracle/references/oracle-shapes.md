# Oracle shapes — the four you can hold

An oracle is any endpoint that answers a question about a ciphertext, a plaintext, or a tag. Before any exploit loop, name exactly which one you hold — encrypt, decrypt, padding-check, or verify — because the attack inventory differs completely per shape.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| You submit bytes, service returns ciphertext | encrypt oracle (ECB/CBC/CTR under a hidden key) | alignment and mode fingerprinting first |
| Service decrypts and returns plaintext or a decode error | full decrypt oracle | usually trivial — request the flag's decryption |
| Service decrypts and only reports validity | padding/validity oracle | padding-oracle decryption loop |
| Service checks a tag you submit | verify oracle | tag-forgery or length-extension test |
| You see ciphertext AND a tag AND a nonce | authenticated bundle | nonce reuse or tag-truncation, not padding |

## Steps

1. Send 32+ identical bytes; identical 16-byte ciphertext blocks confirm ECB.
2. Send two different lengths; a length-preserving output marks CTR/stream, padded output marks ECB/CBC.
3. Corrupt one ciphertext byte; a padding-specific error vs a generic reject separates the oracle kinds.
4. Check whether a tag is verified BEFORE decryption — if yes, the class is closed for malleability attacks.

## Falsifier

Falsifier — the service authenticates before decrypting (GCM tag, or HMAC verified first). A tampered ciphertext is rejected identically for every corruption; no oracle exists to query. Reclassify toward nonce reuse or key-material leaks instead.

## Traps

- A 500-vs-200 pair is not automatically a padding oracle: compare invalid pad vs valid pad/invalid MAC first.
- Gzip/deflate before encryption destroys byte-at-a-time alignment — the ciphertext length stops tracking input length.
- A service that rate-limits at ~10 req/s cannot sustain a 40k-request padding loop; count request budget first.
- Base64 decoders that reject bad padding echo a DIFFERENT error than the crypto layer — read which layer answered.

## Commands

```bash
python3 tools/crypto_attack.py list
python3 tools/ecb_oracle.py --selftest
python3 tools/pad_oracle.py --selftest
```

## Cross-references

`ecb-detection.md` · `cbc-padding-oracle.md` · `ctr-nonce-reuse.md` · `mac-forgery.md` · `../field-notes.md`
