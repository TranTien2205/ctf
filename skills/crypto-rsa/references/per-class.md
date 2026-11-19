# Per-class map — crypto-rsa vs the neighbours

## The neighbours

| Class | The tell that routes there |
|---|---|
| `crypto-ecc-dlog` | `g`, `h=g^x`, a curve, `order`, `dlog` — a discrete-log, not factoring |
| `crypto-prng` | a keystream / generator output — `lcg`,`mt19937`,`lfsr`,`xorshift` |
| `crypto-symmetric-oracle` | a service that encrypts/decrypts/signs — padding oracle, ECB, GCM |
| `crypto-classical` | xor, vigenere, base64, a classical cipher |
| `misc-constraint-puzzle` | a constraint puzzle that uses RSA values |
| `web-*` | a web bug — RSA may appear but the class is the web class |

## The ambiguous edges

- A socket **printing** `n`,`e`,`c` → this class (transport).
- A socket **computing** on `m` → `crypto-symmetric-oracle`.
- A signature service returning a **faulty** sig → `crt` Bellcore (this class).
- A signature service signing arbitrary `m` → the signature-forgery class.
- "decrypt this" with `d`/`phi`/`p`,`q` held → `factor-from-d`/`rsa-decrypt`.
- `g`,`h` and a `pow` construction → `crypto-ecc-dlog`.
- A `n` with an `oracle.py` that decrypts → `crypto-symmetric-oracle` (the
  *decision* is a service).

## The switch rule

- Recover `p`,`q`,`d`,`φ`,`m` from `n`,`e`,`c` → this class.
- Recover `x` from `g^x` → `crypto-ecc-dlog`.
- Recover a stream/seed → `crypto-prng`.
- Abuse a computing oracle → `crypto-symmetric-oracle`.
- Decode a cipher → `crypto-classical`.

## The shared tooling

`tools/crypto_attack.py` serves `crypto-ecc-dlog`, `crypto-prng`,
`crypto-symmetric-oracle` too — `list` names all ids; the RSA subset is the
`fermat`/`wiener`/`boneh-durfee`/`coppersmith`/`batch-gcd`/`common-modulus`/
`small-e`/`nth-root`/`hastad`/`pollard-pm1`/`franklin-reiter`/`crt`/
`factor-from-d`/`rsa-decrypt`/`eth-root` family.
