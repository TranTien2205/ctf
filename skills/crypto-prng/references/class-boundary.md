# Class boundary — stay or leave

## Stay — the shapes here

- A generator's outputs are recoverable → `lcg`/`lfsr`/`mt`/`xorshift`.
- A weak/timestamp seed → enumerable → seed-search.
- The recover is provable by `predict == held-back`.

## Leave — the wrong-class shapes

| Looks like | Actually | Route |
|---|---|---|
| `n, e, c` ints | RSA | `crypto-rsa` |
| `h = g^x`, `d·G` | dlog/ECC | `crypto-ecc-dlog` |
| AES/CBC/GCM/XOR-keyed | symmetric oracle | `crypto-symmetric-oracle` |
| `H(secret||m)` length-ext | `hash_ext` | `crypto-symmetric-oracle` |
| `+/=` hex `01` blob | encoding | `misc-encoding-carrier` |
| `os.urandom`/`secrets`/CSPRNG | truly random | NOT solvable here |

## The grey zone

- **A reused one-time pad / CTR nonce** → `xor.crib_drag` (`tools/crypto/xor.py`)
  — a stream reuse, not a PRNG recovery.
- **A keyed PRF (HMAC/PRF)** → not enumerable, not recoverable → wrong class.
- **`randint`-based token that IS the flag** → the generator recovery is the
  class step; the flag is `impact`.
- **`mt_rand`/`java.util.Random`** → MT/Java-LCG variants — same family,
  different constants — `lcg-*`/`mt19937` patterns with adjusted params.

## The verify test

If no held-back output can be reproduced, the source isn't a predictable
generator here — re-classify.
