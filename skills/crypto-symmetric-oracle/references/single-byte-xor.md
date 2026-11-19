# Single-byte and repeating-key XOR

A byte-XOR cipher is broken by frequency: try all 256 keys, score English-ness. Repeating-key XOR is the same problem after recovering key length by normalized Hamming distance.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Short ciphertext, unknown 1-byte key | single-byte-xor | score all 256 |
| Long ciphertext, periodic key suspected | repeating-key XOR | keysize via Hamming, then per-column single-byte |
| Printable result under some key | candidate | confirm by structure, not score alone |

## Steps

1. python3 tools/crypto_attack.py single-byte-xor --ct <hex> — returns the best-scoring decryptions and keys.
2. For repeating-key: for keysize 2..40 compute normalized Hamming distance between consecutive blocks; the minimum is the keysize.
3. Transpose into keysize columns; single-byte-xor each column; concatenate for the key.
4. Verify the whole plaintext reads coherently — a scoring win on a short text can be a fluke.

## Falsifier

Falsifier — no single-byte key produces mostly printable output AND the repeating-key analysis finds no keysize under ~40 that decodes coherently: the cipher is not XOR-with-short-key. Reclassify to classical or PRNG.

## Traps

- Frequency scoring fails on <20-byte inputs — too little material; try known-structure cribs instead.
- Base64 the ciphertext BEFORE analysis if it arrived encoded — XOR'ing base64 text is the classic own-goal.
- Keysize multiples of the true keysize also score low; prefer the smallest plausible.

## Commands

```bash
python3 tools/crypto_attack.py single-byte-xor --ct <hex>
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'
```

## Cross-references

`crib-drag.md` · `ctr-nonce-reuse.md`
