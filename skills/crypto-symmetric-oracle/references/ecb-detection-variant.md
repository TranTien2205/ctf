# ECB detection — one request, deterministic — surface variants

ECB leaks structure: identical plaintext blocks produce identical ciphertext blocks. Detection needs one request holding enough repeated material to fill two blocks — no statistical test, no second round-trip.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| Identical plaintext block appears twice → identical ciphertext block pair | ECB confirmed | byte-at-a-time or cut-and-paste |
| Repeated input never repeats in output | CBC/CTR/stream or ECB+prefix desync | alignment probe |
| Ciphertext length jumps in block-size steps | block cipher (ECB or CBC) | block-size measurement |
| Ciphertext length tracks input 1:1 | stream cipher or CTR | keystream-reuse test |

## Variant-specific traps

- A fixed server-side prefix shifts your alignment; the duplicate blocks appear offset by prefix_len mod 16.
- CBC with a fixed IV can mimic ECB on the FIRST block only — check pairs past offset 0.
- Compression before encryption makes 'A'*48 compress to nothing — no duplicate ever appears; that is a different challenge (CRIME-style).
- PKCS#7 padding means a 48-byte aligned input pads to 64 — the pad block is constant too and can be mistaken for signal.

## Falsifier

Falsifier — no duplicated 16-byte window appears anywhere in a 48-byte repeated input after ruling out misalignment, and the length grows continuously rather than in block steps: the mode is not ECB.

## Cross-references

`ecb-byte-at-a-time.md` · `ecb-cut-and-paste.md` · `block-alignment.md`
