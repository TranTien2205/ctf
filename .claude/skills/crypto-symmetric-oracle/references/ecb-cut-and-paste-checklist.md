# ECB cut-and-paste / block substitution — operational checklist

ECB blocks are independent: a ciphertext block decrypts the same wherever it sits. Forge a message by swapping, replaying, or re-ordering blocks — the standard target is role/admin fields in encrypted profiles.

## Checklist

- [ ] Map which plaintext fields land in which ciphertext blocks by varying each input one at a time.
- [ ] Craft an input whose LAST block is exactly the value you need (e.g. 'admin' + PKCS#7 pad bytes as literal input text).
- [ ] Request that token, keep the chosen block.
- [ ] Request the real token; replace the target block with the kept one.
- [ ] Verify the forged token decrypts and parses — trailing garbage in the last block is usually tolerated by parsers.

## Abort conditions

- Swapping two middle blocks corrupts NEITHER neighbor under ECB (unlike CBC) — that is the whole point; do not expect error signals.
- If the last block must survive PKCS#7 unpadding, your spliced block must end in valid pad bytes.
- Some services add a checksum block at the end — a splice then fails a CRC, not a MAC; a CRC is itself forgeable but differently.

## Falsifier

Falsifier — the token carries a MAC over the whole ciphertext or the plaintext, or decrypt rejects spliced blocks: the construction is authenticated and cut-and-paste dies. Reclassify to mac-forgery or authenticated-boundary.

## Cross-references

`ecb-detection.md` · `ecb-byte-at-a-time.md` · `token-forgery-workflows.md`
