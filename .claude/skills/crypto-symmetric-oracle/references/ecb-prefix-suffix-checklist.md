# ECB prefix vs suffix oracles — operational checklist

Byte-at-a-time works when your input PRECEDES the secret (suffix). When the secret precedes your input, the method inverts — recover backwards, or via a fixed suffix oracle.

## Checklist

- [ ] Determine which of the three shapes you have by injecting a marker and watching where it lands relative to the fixed blocks.
- [ ] Suffix: standard byte-at-a-time — pad so the unknown byte ends your block.
- [ ] Prefix: recover right-to-left — put your marker AFTER the secret region and build guesses from the tail.
- [ ] Sandwiched: measure both fixed lengths, handle alignment for prefix, then run byte-at-a-time on the suffix.

## Abort conditions

- A random per-request prefix only defeats alignment, not the method — if a fixed suffix exists, attack backwards.
- Prefix recovery is rarer; double-check your orientation before implementing.
- Multiple secrets in one ciphertext can be independent — measure each region separately.

## Falsifier

Falsifier — neither prefix nor suffix is controllable (your input is wholly inside fixed material): the oracle doesn't reach the secret.

## Cross-references

`ecb-byte-at-a-time.md` · `block-alignment.md`
