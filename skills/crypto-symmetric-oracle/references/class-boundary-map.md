# Class boundary — what crypto-symmetric-oracle is NOT — map

| Shape | Real class |
|---|---|
| Modulus/exponent oracle, parity leak | `crypto-rsa` |
| LCG/MT/xorshift keystream, time-seeded | `crypto-prng` |
| Caesar/Vigenère/substitution | `crypto-classical` |
| Base64/hex/rot13 as the whole 'cipher' | `misc-encoding-carrier` |
| Padding oracle inside an HTTP service with a web sink | `web-*` for the sink, this class for the crypto |

Expanded rows and abort conditions: `class-boundary.md` and `class-boundary-deep.md`.
