# Byte-at-a-time ECB decryption — operational checklist

ECB + attacker-controlled prefix = an encryption oracle you can read secrets out of, one byte per position. The classic recipe: keep the secret's first unknown byte at the end of a controlled block, brute that byte through all 256 guesses, advance.

## Checklist

- [ ] Measure block size and secret length: grow input until ciphertext grows; the jump width is the block, the plateau is secret+pad.
- [ ] Hold input = (block-1) bytes; the secret's first byte lands at the block boundary. Store the real ciphertext block.
- [ ] Submit (block-1) bytes + candidate byte; a matching block confirms the byte.
- [ ] Slide the window: input (block-2), guess byte 2 against the known byte-1 context, and so on through the first block.
- [ ] For block N>1, build the guess block from the last 15 recovered bytes; always compare blocks at the same offset.

## Abort conditions

- Off-by-one at block boundaries: when your input is 0 mod block, the unknown byte is in the NEXT block — track absolute positions, not input length.
- A random per-request prefix defeats the method entirely; detect it by submitting the same input twice and diffing.
- PKCS#7: once you hit the pad region the oracle may reject un-pad-like guesses — stop at the measured secret length.

## Falsifier

Falsifier — the recovered plaintext stops being printable/structured partway through, or no candidate ever matches: the mode is not ECB or the 'secret' is encrypted separately (different key or different transform).

## Cross-references

`ecb-detection.md` · `block-alignment.md` · `tools-ecb-oracle.md`
