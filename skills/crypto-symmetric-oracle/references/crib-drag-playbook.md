# Crib-dragging — reading P1 XOR P2 — playbook

With P1 XOR P2 in hand (from a reused keystream), a guessed word in one message reveals the corresponding bytes of the other. Slide the crib across offsets; each hit grows the recovered region.

## Ordered playbook

1. XOR the two ciphertexts (raw bytes, equal length prefix).
2. python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{' — try flag format, HTTP headers, JSON keys, English words.
3. Each confirmed crib at offset o recovers len(crib) bytes of BOTH messages at o.
4. Expand each hit: guess the bytes before/after ('flag{' → the brace content, 'the ' → the following word).
5. Iterate between the two plaintexts until the flag region is fully recovered.

## Falsifier

Falsifier — every offset under every reasonable crib is non-printable in at least one direction: the keystreams were not the same (nonces differ) or the underlying data is binary/compressed.

## Commands

```bash
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'
python3 tools/crypto_attack.py single-byte-xor --ct <h>
```
