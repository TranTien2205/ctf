# HMAC vs raw-hash MAC — the extension boundary — deep

Length extension exists because sha1(secret||m) leaks its chaining state. HMAC wraps the key into two pads and closes that channel. Telling them apart is a one-probe question.

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

Falsifier — the MAC verifies under HMAC construction, or the digest is a sponge: no state leaks to extend. Every extension attempt fails with the same reject.

## Highest-cost traps

- sha256 has a 64-byte block; sha1/md5 also 64 — block size enters the glue-padding formula, not the digest size.
- Truncated SHA-512/256 still extends — the internal state is what matters, and it is fully carried in the output for full-width digests.
- HMAC is closed only when IMPLEMENTED as HMAC — a hand-rolled 'two-layer hash' may still leak.

## Commands

```bash
python3 tools/crypto_attack.py length-extension --help
```

## Cross-references

`length-extension.md` · `mac-forgery.md`
