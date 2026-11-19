# Class boundary — when it's NOT this class

## Confusable classes

| Looks like | Actually | Route |
|---|---|---|
| `n`, `e`, `c` ints | RSA | `crypto-rsa` |
| `aes`/`cbc`/`ecb`/`gcm`/`xor` | symmetric oracle | `crypto-symmetric-oracle` |
| `mt19937`/`lcg`/`lfsr` | PRNG | `crypto-prng` |
| `+/=`/hex/`01`/`.-` blob | encoding | `misc-encoding-carrier` |
| `jwt` with RSA/ECDSA signed | web-token misuse | `web-auth-session` |
| a service *taking* attacker points | could be here (invalid curve) or web | here only if the bug is crypto |

## The ECC/DLog test

This class applies when the answer is a **scalar** — `d`, `x`, or the nonce
`k` that reveals `d`. If the answer is a message or a token, the crypto is
a step, not the class.

## When to stay

- Curve params / sig pairs / dlog statement present.
- The recoverable secret is a scalar.
- `crypto_attack.py` has an attack id that fits.

## When to leave

- The handout is a protocol flow with a broken step, not a crypto primitive
  → re-classify (`crypto-triage` or a web skill).
- The bug is "the server never checks the signature" — web logic flaw.
- `verify` can't possibly hold (no public key supplied, no `g^x` to check)
  → probably not a dlog challenge.
