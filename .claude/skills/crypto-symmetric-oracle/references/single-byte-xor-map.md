# Single-byte and repeating-key XOR — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Short ciphertext, unknown 1-byte key | single-byte-xor | score all 256 |
| Long ciphertext, periodic key suspected | repeating-key XOR | keysize via Hamming, then per-column single-byte |
| Printable result under some key | candidate | confirm by structure, not score alone |

## Falsifier

Falsifier — no single-byte key produces mostly printable output AND the repeating-key analysis finds no keysize under ~40 that decodes coherently: the cipher is not XOR-with-short-key. Reclassify to classical or PRNG.
