# CBC-MAC and MAC-construction flaws

CBC-MAC is secure for fixed-length messages and forgeable for variable-length ones. A CTF classic: given MAC(m), produce MAC(m || m' ) without the key.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| MAC = last CBC block of the message | CBC-MAC | extension splice |
| Variable-length inputs MAC'd | forgery applies | choose the splice |
| Length prepended to message before CBC-MAC | basic splice closed | check other constructions |

## Steps

1. Obtain (m, t) where t = CBC-MAC(m), and your target m_target.
2. Construct m* = m || (m'_1 XOR t) || m'_2...: the last block MACs to t while you control the tail.
3. Submit m* with tag t — acceptance is the forgery.
4. If length-prepended, look for the variant: ECBC/CMAC differences, or whether the length can be manipulated.

## Falsifier

Falsifier — the MAC is CMAC/HMAC or prepends the length safely: the splice is rejected. Reclassify to length-extension or mac-forgery.

## Traps

- CBC-MAC splices need a known (m, t) pair — request one first.
- The patch bytes are XOR'd into the first block of the extension — they must parse in the message format.
- This is NOT hash length-extension: CBC-MAC is a block cipher construction; don't confuse the two tools.

## Commands

```bash
python3 tools/crypto_attack.py list
```

## Cross-references

`mac-forgery.md` · `length-extension.md`
