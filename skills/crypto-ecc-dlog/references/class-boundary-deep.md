# Class boundary deep — when to stay, when to leave

## Stay — the scalar-is-the-answer shapes

- `d`, `x`, or `k` is recoverable from the handout/oracle.
- `crypto_attack.py` has an attack id fitting the observation.
- `x·G == Q`/`g^x == h` can verify the result.

## Leave — the wrong-class shapes

| Looks like | Actually | Route |
|---|---|---|
| `n, e, c` ints, `d = e⁻¹ mod φ(n)` | RSA | `crypto-rsa` |
| `AES`/`CBC`/`GCM`/`XOR`/stream | symmetric | `crypto-symmetric-oracle` |
| `mt19937`/`lcg`/`lfsr`/`rand()` | PRNG | `crypto-prng` |
| `+/=`/hex/`01`/`.-` blob | encoding | `misc-encoding-carrier` |
| `jwt` signature missing check | web-logic | `web-auth-session` |
| hash length extension | `hash_ext` | `crypto-symmetric-oracle` |
| `bleichenbacher`/`parity oracle` | RSA padding | `crypto-rsa` |

## The grey zone

- **A point oracle that validates** — not invalid curve; could be a timing
  or nonce side channel → `hnp-ecdsa` if `k` biased.
- **A DH statement with `x` embedded in protocol** — `x` recovery is here;
  the *use* of `x` (decrypt, derive key) is the flag step.
- **`hash_ext`** — length-extension on `H(secret||m)` — different attack
  (`tools/crypto/hash_ext.py`), not a dlog.
- **Pairing curve with small embedding degree** — MOV/Frey-Rück — no
  pairing tool here; record as intended-path, don't stall.

## The verify test

If `x·G == Q` or `g^x == h` can't be checked (no `Q`, no `h` to verify
against), the shape isn't dlog-shaped — re-classify.
