# Single-byte and repeating-key XOR — operational checklist

A byte-XOR cipher is broken by frequency: try all 256 keys, score English-ness. Repeating-key XOR is the same problem after recovering key length by normalized Hamming distance.

## Checklist

- [ ] python3 tools/crypto_attack.py single-byte-xor --ct <hex> — returns the best-scoring decryptions and keys.
- [ ] For repeating-key: for keysize 2..40 compute normalized Hamming distance between consecutive blocks; the minimum is the keysize.
- [ ] Transpose into keysize columns; single-byte-xor each column; concatenate for the key.
- [ ] Verify the whole plaintext reads coherently — a scoring win on a short text can be a fluke.

## Abort conditions

- Frequency scoring fails on <20-byte inputs — too little material; try known-structure cribs instead.
- Base64 the ciphertext BEFORE analysis if it arrived encoded — XOR'ing base64 text is the classic own-goal.
- Keysize multiples of the true keysize also score low; prefer the smallest plausible.

## Falsifier

Falsifier — no single-byte key produces mostly printable output AND the repeating-key analysis finds no keysize under ~40 that decodes coherently: the cipher is not XOR-with-short-key. Reclassify to classical or PRNG.

## Cross-references

`crib-drag.md` · `ctr-nonce-reuse.md`
