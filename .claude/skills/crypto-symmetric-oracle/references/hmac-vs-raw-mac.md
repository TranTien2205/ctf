# HMAC vs raw-hash MAC — the extension boundary

Length extension exists because sha1(secret||m) leaks its chaining state. HMAC wraps the key into two pads and closes that channel. Telling them apart is a one-probe question.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| MAC construction visible in source as H(secret||m) | raw prefix MAC | length-extension |
| Source shows hmac.new / HMAC( | HMAC — extension closed | look for key leaks or nonce reuse |
| MAC over m||secret (suffix) | extension the wrong direction | usually safe — check for confusion |
| Hash named sha3/blake2/keccak | sponge — no MD state to extend | reclassify |

## Steps

1. Name the hash from source or from the digest length/shape (sha1=40 hex, sha256=64, md5=32).
2. Name the construction: H(s||m), H(m||s), HMAC(k,m), or keyed-sponge.
3. Only H(s||m) over a Merkle-Damgard hash with no post-MAC data is extendable.
4. When source is absent, probe: request MAC of m, then submit m||pad||append with the extension-fitted MAC — one request answers.

## Falsifier

Falsifier — the MAC verifies under HMAC construction, or the digest is a sponge: no state leaks to extend. Every extension attempt fails with the same reject.

## Traps

- sha256 has a 64-byte block; sha1/md5 also 64 — block size enters the glue-padding formula, not the digest size.
- Truncated SHA-512/256 still extends — the internal state is what matters, and it is fully carried in the output for full-width digests.
- HMAC is closed only when IMPLEMENTED as HMAC — a hand-rolled 'two-layer hash' may still leak.

## Commands

```bash
python3 tools/crypto_attack.py length-extension --help
```

## Cross-references

`length-extension.md` · `mac-forgery.md`
