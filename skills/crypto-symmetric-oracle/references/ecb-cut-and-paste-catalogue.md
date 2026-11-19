# ECB cut-and-paste / block substitution — case catalogue

ECB blocks are independent: a ciphertext block decrypts the same wherever it sits. Forge a message by swapping, replaying, or re-ordering blocks — the standard target is role/admin fields in encrypted profiles.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Encrypted token is a concatenation of blocks, each a field | block substitution applies | map field offsets, then splice |
| 2 | You can request tokens for chosen input values | chosen-plaintext block source | mint a block holding the value you need |
| 3 | Token has a fixed prefix you cannot change | boundary alignment needed | pad your input so the target field starts a block |

## Falsifier

Falsifier — the token carries a MAC over the whole ciphertext or the plaintext, or decrypt rejects spliced blocks: the construction is authenticated and cut-and-paste dies. Reclassify to mac-forgery or authenticated-boundary.

## Coverage notes

- Swapping two middle blocks corrupts NEITHER neighbor under ECB (unlike CBC) — that is the whole point; do not expect error signals.
- If the last block must survive PKCS#7 unpadding, your spliced block must end in valid pad bytes.
- Some services add a checksum block at the end — a splice then fails a CRC, not a MAC; a CRC is itself forgeable but differently.
- Duplicate-block replay works even when you cannot mint chosen blocks: copy an existing 'admin' block from another token.

## Cross-references

`ecb-detection.md` · `ecb-byte-at-a-time.md` · `token-forgery-workflows.md`
