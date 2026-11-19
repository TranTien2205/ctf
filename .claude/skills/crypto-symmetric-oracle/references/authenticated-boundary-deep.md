# Authenticated modes — where the class closes — deep

GCM, ChaCha20-Poly1305, and encrypt-then-MAC kill every malleability oracle. The honest skill boundary: recognize when NOTHING here applies and route out early.

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

Falsifier — corrupt ciphertext is rejected identically for every offset tested: the class is closed. Continuing to probe malleability is budget waste.

## Highest-cost traps

- Constant-time compare makes TIMING identical too — do not confuse 'no timing signal' with 'bug present'.
- A 96-bit GCM nonce with random generation collides after ~2^32 messages — rarely reachable in CTF scale.
- Some CTF handouts label the mode 'AES-256' without the mode — check ciphertext length vs plaintext length and tag presence.

## Commands

```bash
python3 tools/crypto_attack.py list
python3 tools/gcm_nonce.py --selftest
```

## Cross-references

`oracle-shapes.md` · `gcm-nonce-reuse.md` · `class-boundary.md`
