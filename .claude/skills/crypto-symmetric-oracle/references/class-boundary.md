# Class boundary — what crypto-symmetric-oracle is NOT

The class covers oracles into symmetric constructions. It ends where the
oracle stops being symmetric or stops being an oracle.

## Out — route elsewhere

| Shape | Real class |
|---|---|
| Modulus/exponent oracle, parity leak | `crypto-rsa` |
| LCG/MT/xorshift keystream, time-seeded | `crypto-prng` |
| Caesar/Vigenère/substitution | `crypto-classical` |
| Base64/hex/rot13 as the whole 'cipher' | `misc-encoding-carrier` |
| Padding oracle inside an HTTP service with a web sink | `web-*` for the sink, this class for the crypto |

## Confusables (from the registry)

- `crypto-prng` — both produce keystream-like material. The difference: this
  class assumes a real cipher with an oracle; PRNG assumes a predictable
  generator. Check for a recoverable seed/state first — that is the cheaper
  attack.
- `misc-encoding-carrier` — a blob that decodes without crypto is encoding;
  try decode before assuming cipher.

## The boundary question

'Do I need an oracle loop, or is the material directly readable?' If the
answer is readable → this class. If it is a generator's output → crypto-prng.
If it is a puzzle encoding → misc-encoding-carrier.

## Authenticated boundary

A tag checked before decryption closes the class for malleability. What
remains is nonce-reuse (still this class) or key-path (the class's key-
recovery edge, see `key-path.md`).
