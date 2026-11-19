# Crib-dragging — reading P1 XOR P2 — case catalogue

With P1 XOR P2 in hand (from a reused keystream), a guessed word in one message reveals the corresponding bytes of the other. Slide the crib across offsets; each hit grows the recovered region.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | P1 XOR P2 contains printable-on-both-sides at some offset | valid crib hit | extend left and right |
| 2 | Crib produces gibberish everywhere | crib absent at all offsets | try common protocol words |
| 3 | Both messages partially known | stitch: each crib confirms the other | iterate the loop |

## Falsifier

Falsifier — every offset under every reasonable crib is non-printable in at least one direction: the keystreams were not the same (nonces differ) or the underlying data is binary/compressed.

## Coverage notes

- XOR of two printable ASCII chars is usually NON-printable — 'printable output' is the wrong oracle at the wrong layer: check that BOTH directions decode sanely.
- Spaces: ' ' XOR letter flips case — a classic crib-drag heuristic, implemented inside the tool.
- Compressed plaintext kills crib-dragging: 'flag{' never literally appears. Check for gzip/zlib first.

## Cross-references

`ctr-nonce-reuse.md` · `single-byte-xor.md`
