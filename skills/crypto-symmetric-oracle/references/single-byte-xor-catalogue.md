# Single-byte and repeating-key XOR — case catalogue

A byte-XOR cipher is broken by frequency: try all 256 keys, score English-ness. Repeating-key XOR is the same problem after recovering key length by normalized Hamming distance.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Short ciphertext, unknown 1-byte key | single-byte-xor | score all 256 |
| 2 | Long ciphertext, periodic key suspected | repeating-key XOR | keysize via Hamming, then per-column single-byte |
| 3 | Printable result under some key | candidate | confirm by structure, not score alone |

## Falsifier

Falsifier — no single-byte key produces mostly printable output AND the repeating-key analysis finds no keysize under ~40 that decodes coherently: the cipher is not XOR-with-short-key. Reclassify to classical or PRNG.

## Coverage notes

- Frequency scoring fails on <20-byte inputs — too little material; try known-structure cribs instead.
- Base64 the ciphertext BEFORE analysis if it arrived encoded — XOR'ing base64 text is the classic own-goal.
- Keysize multiples of the true keysize also score low; prefer the smallest plausible.

## Cross-references

`crib-drag.md` · `ctr-nonce-reuse.md`
