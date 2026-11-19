# Crib-dragging — reading P1 XOR P2 — operational checklist

With P1 XOR P2 in hand (from a reused keystream), a guessed word in one message reveals the corresponding bytes of the other. Slide the crib across offsets; each hit grows the recovered region.

## Checklist

- [ ] XOR the two ciphertexts (raw bytes, equal length prefix).
- [ ] python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{' — try flag format, HTTP headers, JSON keys, English words.
- [ ] Each confirmed crib at offset o recovers len(crib) bytes of BOTH messages at o.
- [ ] Expand each hit: guess the bytes before/after ('flag{' → the brace content, 'the ' → the following word).
- [ ] Iterate between the two plaintexts until the flag region is fully recovered.

## Abort conditions

- XOR of two printable ASCII chars is usually NON-printable — 'printable output' is the wrong oracle at the wrong layer: check that BOTH directions decode sanely.
- Spaces: ' ' XOR letter flips case — a classic crib-drag heuristic, implemented inside the tool.
- Compressed plaintext kills crib-dragging: 'flag{' never literally appears. Check for gzip/zlib first.

## Falsifier

Falsifier — every offset under every reasonable crib is non-printable in at least one direction: the keystreams were not the same (nonces differ) or the underlying data is binary/compressed.

## Cross-references

`ctr-nonce-reuse.md` · `single-byte-xor.md`
