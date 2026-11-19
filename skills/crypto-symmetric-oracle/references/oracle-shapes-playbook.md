# Oracle shapes — the four you can hold — playbook

An oracle is any endpoint that answers a question about a ciphertext, a plaintext, or a tag. Before any exploit loop, name exactly which one you hold — encrypt, decrypt, padding-check, or verify — because the attack inventory differs completely per shape.

## Ordered playbook

1. Send 32+ identical bytes; identical 16-byte ciphertext blocks confirm ECB.
2. Send two different lengths; a length-preserving output marks CTR/stream, padded output marks ECB/CBC.
3. Corrupt one ciphertext byte; a padding-specific error vs a generic reject separates the oracle kinds.
4. Check whether a tag is verified BEFORE decryption — if yes, the class is closed for malleability attacks.

## Falsifier

Falsifier — the service authenticates before decrypting (GCM tag, or HMAC verified first). A tampered ciphertext is rejected identically for every corruption; no oracle exists to query. Reclassify toward nonce reuse or key-material leaks instead.

## Commands

```bash
python3 tools/crypto_attack.py list
python3 tools/ecb_oracle.py --selftest
python3 tools/pad_oracle.py --selftest
```
