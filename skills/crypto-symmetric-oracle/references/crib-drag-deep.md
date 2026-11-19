# Crib-dragging — reading P1 XOR P2 — deep

With P1 XOR P2 in hand (from a reused keystream), a guessed word in one message reveals the corresponding bytes of the other. Slide the crib across offsets; each hit grows the recovered region.

## Mechanism internals

The attack surface is defined by which byte the service lets you reach and which bit of the response leaks. The three invariants that hold across every variant of this attack: (1) the distinguisher must be measurable before the loop starts, (2) each recovered byte is confirmed by an exact-match answer — never a probabilistic one, (3) the loop stops at the measured boundary (block edge, secret length, tag width), not where the bytes 'look done'.

## Boundary conditions

- If the response is compressed before encryption, alignment dies — check for gzip/deflate first.
- If the oracle answers 'ok' for structurally invalid input, the parser layer is the bug, not the crypto.
- Rate limits convert a 40k-request loop into days — measure throughput and bound --max-requests.
- Nonce reuse at the block level is different from per-message reuse — align by absolute counter.
- A MAC checked before decryption closes every malleability route in this file.
- When the same tool flag is documented differently in two modules, tools/<name>.py --help is authoritative.

## Falsifier

Falsifier — every offset under every reasonable crib is non-printable in at least one direction: the keystreams were not the same (nonces differ) or the underlying data is binary/compressed.

## Highest-cost traps

- XOR of two printable ASCII chars is usually NON-printable — 'printable output' is the wrong oracle at the wrong layer: check that BOTH directions decode sanely.
- Spaces: ' ' XOR letter flips case — a classic crib-drag heuristic, implemented inside the tool.
- Compressed plaintext kills crib-dragging: 'flag{' never literally appears. Check for gzip/zlib first.

## Commands

```bash
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'
python3 tools/crypto_attack.py single-byte-xor --ct <h>
```

## Cross-references

`ctr-nonce-reuse.md` · `single-byte-xor.md`
