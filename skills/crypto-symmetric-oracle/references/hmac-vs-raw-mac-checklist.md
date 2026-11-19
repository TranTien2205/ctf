# HMAC vs raw-hash MAC — the extension boundary — operational checklist

Length extension exists because sha1(secret||m) leaks its chaining state. HMAC wraps the key into two pads and closes that channel. Telling them apart is a one-probe question.

## Checklist

- [ ] Name the hash from source or from the digest length/shape (sha1=40 hex, sha256=64, md5=32).
- [ ] Name the construction: H(s||m), H(m||s), HMAC(k,m), or keyed-sponge.
- [ ] Only H(s||m) over a Merkle-Damgard hash with no post-MAC data is extendable.
- [ ] When source is absent, probe: request MAC of m, then submit m||pad||append with the extension-fitted MAC — one request answers.

## Abort conditions

- sha256 has a 64-byte block; sha1/md5 also 64 — block size enters the glue-padding formula, not the digest size.
- Truncated SHA-512/256 still extends — the internal state is what matters, and it is fully carried in the output for full-width digests.
- HMAC is closed only when IMPLEMENTED as HMAC — a hand-rolled 'two-layer hash' may still leak.

## Falsifier

Falsifier — the MAC verifies under HMAC construction, or the digest is a sponge: no state leaks to extend. Every extension attempt fails with the same reject.

## Cross-references

`length-extension.md` · `mac-forgery.md`
