# Class boundary — where crypto-rsa ends and the neighbours begin

## The defining line

`crypto-rsa` is **integer factorisation / RSA private-value recovery** — `n`,`e`,
`c` and a private value to recover. The boundary is whether the problem is a
factoring problem.

## The neighbours

| Neighbour | The tell that routes away |
|---|---|
| `crypto-ecc-dlog` | `g`,`h=g^x`,a curve,`order`,`dlog` — a discrete-log, not factoring. `bsgs`,`pohlig-hellman`,`smart_attack`,`singular_ec`. |
| `crypto-prng` | a keystream / generator output — `lcg`,`mt19937`,`lfsr`,`xorshift`. No modulus. |
| `crypto-symmetric-oracle` | a *service* that encrypts/decrypts/signs — padding oracle,ECB,GCM,length-extension. Numbers → `crypto-rsa`; a *function* → oracle. |
| `crypto-classical` | xor,vigenere,base64,a classical cipher — no `n`,`e`. |
| `misc-constraint-puzzle` | a constraint puzzle that *uses* RSA values but asks a property, not a recovery. |
| `web-*` | a web bug — RSA may appear but the class is the web class. |

## The ambiguous edges

- A socket that *prints* `n`,`e`,`c` → this class (transport, not oracle).
- A socket that *computes* on your `m` → `crypto-symmetric-oracle`.
- A signature service → if it returns a *faulty* sig → `crt` Bellcore (this
  class); if it signs arbitrary `m` → the signature-forgery class, not this.
- A "decrypt this" with `d`/`φ`/`p`/`q` held → `factor-from-d`/`rsa-decrypt`
  (this class terminal).
- An `n` with a `g`,`h` and a `pow` construction → `crypto-ecc-dlog`, not RSA.

## The switch rule

When the handout names `n`,`e`,`c` and a private value to recover → stay. When
it names `g`,`h`,a curve,or a group element → `crypto-ecc-dlog`. When it is a
service that computes → `crypto-symmetric-oracle`. When it is a keystream →
`crypto-prng`.
