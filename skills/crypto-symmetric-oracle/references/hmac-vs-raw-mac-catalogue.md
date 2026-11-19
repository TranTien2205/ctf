# HMAC vs raw-hash MAC — the extension boundary — case catalogue

Length extension exists because sha1(secret||m) leaks its chaining state. HMAC wraps the key into two pads and closes that channel. Telling them apart is a one-probe question.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | MAC construction visible in source as H(secret||m) | raw prefix MAC | length-extension |
| 2 | Source shows hmac.new / HMAC( | HMAC — extension closed | look for key leaks or nonce reuse |
| 3 | MAC over m||secret (suffix) | extension the wrong direction | usually safe — check for confusion |
| 4 | Hash named sha3/blake2/keccak | sponge — no MD state to extend | reclassify |

## Falsifier

Falsifier — the MAC verifies under HMAC construction, or the digest is a sponge: no state leaks to extend. Every extension attempt fails with the same reject.

## Coverage notes

- sha256 has a 64-byte block; sha1/md5 also 64 — block size enters the glue-padding formula, not the digest size.
- Truncated SHA-512/256 still extends — the internal state is what matters, and it is fully carried in the output for full-width digests.
- HMAC is closed only when IMPLEMENTED as HMAC — a hand-rolled 'two-layer hash' may still leak.

## Cross-references

`length-extension.md` · `mac-forgery.md`
