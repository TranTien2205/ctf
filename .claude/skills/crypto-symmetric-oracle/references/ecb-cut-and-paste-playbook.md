# ECB cut-and-paste / block substitution — playbook

ECB blocks are independent: a ciphertext block decrypts the same wherever it sits. Forge a message by swapping, replaying, or re-ordering blocks — the standard target is role/admin fields in encrypted profiles.

## Ordered playbook

1. Map which plaintext fields land in which ciphertext blocks by varying each input one at a time.
2. Craft an input whose LAST block is exactly the value you need (e.g. 'admin' + PKCS#7 pad bytes as literal input text).
3. Request that token, keep the chosen block.
4. Request the real token; replace the target block with the kept one.
5. Verify the forged token decrypts and parses — trailing garbage in the last block is usually tolerated by parsers.

## Falsifier

Falsifier — the token carries a MAC over the whole ciphertext or the plaintext, or decrypt rejects spliced blocks: the construction is authenticated and cut-and-paste dies. Reclassify to mac-forgery or authenticated-boundary.

## Commands

```bash
python3 tools/ecb_oracle.py --selftest
```
