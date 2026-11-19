# CBC-MAC and MAC-construction flaws — operational checklist

CBC-MAC is secure for fixed-length messages and forgeable for variable-length ones. A CTF classic: given MAC(m), produce MAC(m || m' ) without the key.

## Checklist

- [ ] Obtain (m, t) where t = CBC-MAC(m), and your target m_target.
- [ ] Construct m* = m || (m'_1 XOR t) || m'_2...: the last block MACs to t while you control the tail.
- [ ] Submit m* with tag t — acceptance is the forgery.
- [ ] If length-prepended, look for the variant: ECBC/CMAC differences, or whether the length can be manipulated.

## Abort conditions

- CBC-MAC splices need a known (m, t) pair — request one first.
- The patch bytes are XOR'd into the first block of the extension — they must parse in the message format.
- This is NOT hash length-extension: CBC-MAC is a block cipher construction; don't confuse the two tools.

## Falsifier

Falsifier — the MAC is CMAC/HMAC or prepends the length safely: the splice is rejected. Reclassify to length-extension or mac-forgery.

## Cross-references

`mac-forgery.md` · `length-extension.md`
