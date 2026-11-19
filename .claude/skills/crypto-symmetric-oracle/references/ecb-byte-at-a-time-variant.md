# Byte-at-a-time ECB decryption — surface variants

ECB + attacker-controlled prefix = an encryption oracle you can read secrets out of, one byte per position. The classic recipe: keep the secret's first unknown byte at the end of a controlled block, brute that byte through all 256 guesses, advance.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| You control a prefix position before a hidden secret in the same plaintext | byte-at-a-time applies | alignment then the guess loop |
| Appended secret length measurable by growing input | secret length recoverable | boundary measurement |
| Random prefix before your input | alignment breaks | find the fixed suffix or give up ECB |

## Variant-specific traps

- Off-by-one at block boundaries: when your input is 0 mod block, the unknown byte is in the NEXT block — track absolute positions, not input length.
- A random per-request prefix defeats the method entirely; detect it by submitting the same input twice and diffing.
- PKCS#7: once you hit the pad region the oracle may reject un-pad-like guesses — stop at the measured secret length.
- tools/ecb_oracle.py drives exactly this loop over HTTP; hand-rolling it means re-sending the prefix alignment yourself.

## Falsifier

Falsifier — the recovered plaintext stops being printable/structured partway through, or no candidate ever matches: the mode is not ECB or the 'secret' is encrypted separately (different key or different transform).

## Cross-references

`ecb-detection.md` · `block-alignment.md` · `tools-ecb-oracle.md`
