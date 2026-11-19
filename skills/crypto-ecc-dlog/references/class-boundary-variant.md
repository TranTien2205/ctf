# Class boundary variant — stay/leave, restated

## Stay — the shapes here

- Scalar `d`/`x`/`k` recoverable from the artifact.
- `x·G == Q`/`g^x == h` verifiable.
- `crypto_attack.py` id or `tools/crypto/*.py` fits.

## Leave — the shapes elsewhere

| Looks like | Route |
|---|---|
| `n e c` | `crypto-rsa` |
| AES/XOR/keystream | `crypto-symmetric-oracle` |
| mt19937/lcg/lfsr | `crypto-prng` |
| b64/hex blob | `misc-encoding-carrier` |
| jwt alg=none | `web-auth-session` |
| hash_ext | `crypto-symmetric-oracle` |

## The grey zone resolved

- `d` recoverable + `d` decrypts → crypto step here, decrypt is the flag step.
- `x` in a DH protocol → `x` recovery here; the DH use is the flag step.
- `hash_ext`/`parity` oracles → other classes, not dlog.
- pairing curves → named, not tooled here.
