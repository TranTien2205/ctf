# Single-byte and repeating-key XOR — summary

A byte-XOR cipher is broken by frequency: try all 256 keys, score English-ness. Repeating-key XOR is the same problem after recovering key length by normalized Hamming distance.

## Signal → route

- Short ciphertext, unknown 1-byte key → score all 256
- Long ciphertext, periodic key suspected → keysize via Hamming, then per-column single-byte
- Printable result under some key → confirm by structure, not score alone

## Falsifier

Falsifier — no single-byte key produces mostly printable output AND the repeating-key analysis finds no keysize under ~40 that decodes coherently: the cipher is not XOR-with-short-key. Reclassify to classical or PRNG.
