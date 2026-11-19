# CBC-MAC and MAC-construction flaws — case catalogue

CBC-MAC is secure for fixed-length messages and forgeable for variable-length ones. A CTF classic: given MAC(m), produce MAC(m || m' ) without the key.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | MAC = last CBC block of the message | CBC-MAC | extension splice |
| 2 | Variable-length inputs MAC'd | forgery applies | choose the splice |
| 3 | Length prepended to message before CBC-MAC | basic splice closed | check other constructions |

## Falsifier

Falsifier — the MAC is CMAC/HMAC or prepends the length safely: the splice is rejected. Reclassify to length-extension or mac-forgery.

## Coverage notes

- CBC-MAC splices need a known (m, t) pair — request one first.
- The patch bytes are XOR'd into the first block of the extension — they must parse in the message format.
- This is NOT hash length-extension: CBC-MAC is a block cipher construction; don't confuse the two tools.

## Cross-references

`mac-forgery.md` · `length-extension.md`
