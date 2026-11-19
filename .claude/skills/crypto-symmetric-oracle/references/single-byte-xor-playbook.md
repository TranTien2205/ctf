# Single-byte and repeating-key XOR — playbook

A byte-XOR cipher is broken by frequency: try all 256 keys, score English-ness. Repeating-key XOR is the same problem after recovering key length by normalized Hamming distance.

## Ordered playbook

1. python3 tools/crypto_attack.py single-byte-xor --ct <hex> — returns the best-scoring decryptions and keys.
2. For repeating-key: for keysize 2..40 compute normalized Hamming distance between consecutive blocks; the minimum is the keysize.
3. Transpose into keysize columns; single-byte-xor each column; concatenate for the key.
4. Verify the whole plaintext reads coherently — a scoring win on a short text can be a fluke.

## Falsifier

Falsifier — no single-byte key produces mostly printable output AND the repeating-key analysis finds no keysize under ~40 that decodes coherently: the cipher is not XOR-with-short-key. Reclassify to classical or PRNG.

## Commands

```bash
python3 tools/crypto_attack.py single-byte-xor --ct <hex>
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'
```
